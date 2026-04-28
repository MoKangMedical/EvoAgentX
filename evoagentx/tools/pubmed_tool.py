"""
PubMed Search Tool for EvoAgentX

Provides PubMed literature search capabilities integrated with the EvoAgentX
tool framework. Based on NCBI E-utilities API.

Integration points:
- MetaForge: Shares PubMedClient for systematic review workflows
- MediChat-RD: Rare disease literature retrieval
- DrugMind: Drug-related publication search

Usage:
    tool = PubMedSearchTool()
    results = tool(query="rare disease gene therapy", max_results=10)
"""

import json
import os
import time
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import urlencode

from .tool import Tool, Toolkit


class PubMedSearchTool(Tool):
    """Search PubMed for biomedical literature using NCBI E-utilities API."""

    name: str = "pubmed_search"
    description: str = (
        "Search PubMed for biomedical literature. Returns article titles, "
        "authors, abstracts, PMIDs, publication dates, and journal info. "
        "Supports MeSH terms, boolean operators (AND, OR, NOT), and field tags "
        "[tiab], [ti], [au], [mh]. Useful for medical research, systematic "
        "reviews, drug studies, and clinical evidence gathering."
    )
    inputs: dict[str, dict[str, Any]] = {
        "query": {
            "type": "string",
            "description": (
                "PubMed search query. Supports MeSH terms, boolean operators "
                "(AND, OR, NOT), field tags [tiab], [ti], [au], [mh]. "
                "Example: 'rare disease AND gene therapy[tiab] AND 2023:2025[dp]'"
            )
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum number of results to return (default 10, max 200)"
        },
        "sort": {
            "type": "string",
            "description": "Sort order: 'relevance' (default), 'date', 'first_author'"
        }
    }
    required: list[str] | None = ["query"]

    def __init__(self, email: str = "", api_key: str = "", **kwargs):
        super().__init__(**kwargs)
        self.email = email or os.getenv("NCBI_EMAIL", "user@evoagentx.med")
        self.api_key = api_key or os.getenv("NCBI_API_KEY", "")
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.last_request_time = 0
        self._ns = {"pubmed": "http://www.ncbi.nlm.nih.gov/pubmed"}

    def _rate_limit(self):
        """NCBI rate limit: 3 req/s without key, 10 req/s with key."""
        min_interval = 0.34 if not self.api_key else 0.1
        elapsed = time.time() - self.last_request_time
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: dict) -> str:
        """Make a request to NCBI E-utilities."""
        import urllib.error
        import urllib.request

        params["tool"] = "evoagentx"
        params["email"] = self.email
        if self.api_key:
            params["api_key"] = self.api_key

        self._rate_limit()
        url = f"{self.base_url}/{endpoint}?{urlencode(params)}"

        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "EvoAgentX/0.1 (medical-ai-framework)"
                })
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return resp.read().decode("utf-8")
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 2:
                    time.sleep(2 ** attempt)
                    continue
                raise
            except Exception:
                if attempt < 2:
                    time.sleep(1)
                    continue
                raise

    def search(self, query: str, max_results: int = 10,
               sort: str = "relevance") -> dict[str, Any]:
        """Search PubMed and return structured results."""
        max_results = min(max_results, 200)

        sort_map = {
            "relevance": "relevance",
            "date": "pub_date",
            "first_author": "first_author"
        }
        sort_param = sort_map.get(sort, "relevance")

        # Step 1: ESearch - get PMIDs
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": sort_param,
            "usehistory": "y"
        }
        search_xml = self._make_request("esearch.fcgi", search_params)

        # Parse JSON response
        try:
            search_data = json.loads(search_xml)
            result = search_data.get("esearchresult", {})
            pmids = result.get("idlist", [])
            total_count = int(result.get("count", 0))
            web_env = result.get("webenv", "")
            query_key = result.get("querykey", "")
        except json.JSONDecodeError:
            # Fallback: parse XML
            root = ET.fromstring(search_xml)
            pmids = [id_el.text for id_el in root.findall(".//Id")]
            total_count = int(root.findtext("Count", "0"))
            web_env = root.findtext("WebEnv", "")
            query_key = root.findtext("QueryKey", "")

        if not pmids:
            return {
                "query": query,
                "total_count": 0,
                "returned": 0,
                "articles": []
            }

        # Step 2: EFetch - get article details
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "rettype": "abstract"
        }
        fetch_xml = self._make_request("efetch.fcgi", fetch_params)
        articles = self._parse_articles(fetch_xml)

        return {
            "query": query,
            "total_count": total_count,
            "returned": len(articles),
            "articles": articles
        }

    def _parse_articles(self, xml_text: str) -> list[dict[str, Any]]:
        """Parse PubMed XML into structured article dicts."""
        root = ET.fromstring(xml_text)
        articles = []

        for article_el in root.findall(".//PubmedArticle"):
            try:
                medline = article_el.find("MedlineCitation")
                article = medline.find("Article")

                # PMID
                pmid = medline.findtext("PMID", "")

                # Title
                title = article.findtext("ArticleTitle", "")

                # Abstract
                abstract_parts = []
                abstract_el = article.find("Abstract")
                if abstract_el is not None:
                    for abs_text in abstract_el.findall("AbstractText"):
                        label = abs_text.get("Label", "")
                        text = abs_text.text or ""
                        if label:
                            abstract_parts.append(f"{label}: {text}")
                        else:
                            abstract_parts.append(text)
                abstract = " ".join(abstract_parts)

                # Authors
                authors = []
                author_list = article.find("AuthorList")
                if author_list is not None:
                    for author in author_list.findall("Author"):
                        last = author.findtext("LastName", "")
                        first = author.findtext("ForeName", "")
                        if last:
                            authors.append(f"{last} {first}".strip())

                # Journal
                journal_el = article.find("Journal")
                journal = journal_el.findtext("Title", "") if journal_el is not None else ""
                journal_abbr = journal_el.findtext("ISOAbbreviation", "") if journal_el is not None else ""

                # Date
                pub_date = ""
                if journal_el is not None:
                    journal_issue = journal_el.find("JournalIssue")
                    if journal_issue is not None:
                        date_el = journal_issue.find("PubDate")
                        if date_el is not None:
                            year = date_el.findtext("Year", "")
                            month = date_el.findtext("Month", "")
                            day = date_el.findtext("Day", "")
                            pub_date = f"{year}-{month}-{day}".strip("-")

                # DOI
                doi = ""
                for eid in article_el.findall(".//ArticleId"):
                    if eid.get("IdType") == "doi":
                        doi = eid.text or ""
                        break

                # MeSH terms
                mesh_terms = []
                mesh_list = medline.find("MeshHeadingList")
                if mesh_list is not None:
                    for heading in mesh_list.findall("MeshHeading"):
                        descriptor = heading.find("DescriptorName")
                        if descriptor is not None:
                            mesh_terms.append(descriptor.text or "")

                articles.append({
                    "pmid": pmid,
                    "title": title,
                    "abstract": abstract[:500] + "..." if len(abstract) > 500 else abstract,
                    "authors": authors[:5],
                    "journal": journal,
                    "journal_abbr": journal_abbr,
                    "pub_date": pub_date,
                    "doi": doi,
                    "mesh_terms": mesh_terms[:10],
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })
            except Exception:
                continue

        return articles

    def __call__(self, query: str, max_results: int = 10,
                 sort: str = "relevance") -> str:
        """Execute PubMed search and return formatted results."""
        results = self.search(query, max_results, sort)

        if not results["articles"]:
            return f"No PubMed results found for: {query}"

        lines = [
            f"PubMed Search: '{query}'",
            f"Total results: {results['total_count']}, showing {results['returned']}",
            ""
        ]

        for i, art in enumerate(results["articles"], 1):
            lines.append(f"[{i}] PMID:{art['pmid']} | {art['pub_date']}")
            lines.append(f"    Title: {art['title']}")
            lines.append(f"    Authors: {', '.join(art['authors'])}")
            lines.append(f"    Journal: {art['journal_abbr']}")
            if art['doi']:
                lines.append(f"    DOI: {art['doi']}")
            if art['mesh_terms']:
                lines.append(f"    MeSH: {', '.join(art['mesh_terms'][:5])}")
            lines.append(f"    URL: {art['url']}")
            lines.append("")

        return "\n".join(lines)


class PubMedFetchDetailTool(Tool):
    """Fetch full details for a specific PubMed article by PMID."""

    name: str = "pubmed_fetch_detail"
    description: str = (
        "Fetch detailed information for a specific PubMed article by PMID. "
        "Returns full abstract, all authors, MeSH terms, keywords, "
        "publication types, and grant info."
    )
    inputs: dict[str, dict[str, Any]] = {
        "pmid": {
            "type": "string",
            "description": "PubMed ID (PMID) of the article to fetch"
        }
    }
    required: list[str] | None = ["pmid"]

    def __init__(self, email: str = "", api_key: str = "", **kwargs):
        super().__init__(**kwargs)
        self._search_tool = PubMedSearchTool(email=email, api_key=api_key)

    def __call__(self, pmid: str) -> str:
        """Fetch article details by PMID."""
        fetch_params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml",
            "rettype": "abstract"
        }
        xml_text = self._search_tool._make_request("efetch.fcgi", fetch_params)
        articles = self._search_tool._parse_articles(xml_text)

        if not articles:
            return f"No article found for PMID: {pmid}"

        art = articles[0]
        return (
            f"PMID: {art['pmid']}\n"
            f"Title: {art['title']}\n"
            f"Authors: {', '.join(art['authors'])}\n"
            f"Journal: {art['journal']} ({art['journal_abbr']})\n"
            f"Date: {art['pub_date']}\n"
            f"DOI: {art['doi']}\n"
            f"MeSH: {', '.join(art['mesh_terms'])}\n"
            f"Abstract: {art['abstract']}\n"
            f"URL: {art['url']}"
        )


class PubMedSearchToolkit(Toolkit):
    """Toolkit combining PubMed search and detail fetch."""

    name: str = "pubmed_toolkit"
    description: str = (
        "PubMed literature search toolkit for biomedical research. "
        "Search and retrieve articles from PubMed/NCBI database. "
        "Supports MeSH terms, boolean queries, and detailed article retrieval."
    )

    def __init__(self, email: str = "", api_key: str = "", **kwargs):
        tools = [
            PubMedSearchTool(email=email, api_key=api_key),
            PubMedFetchDetailTool(email=email, api_key=api_key),
        ]
        super().__init__(tools=tools, **kwargs)
