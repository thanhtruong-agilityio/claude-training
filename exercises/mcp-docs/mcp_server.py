from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from pydantic import Field

mcp = FastMCP("DocumentMCP", log_level="ERROR")

docs = {
    "plan.md": "the plan outlines the steps for the rollout. first migrate the data. then switch traffic.",
    "report.pdf": "The report covers Q3 uptime. Uptime was 99.9 percent.",
    "spec.txt": "The service must respond within 200 ms.",
}


@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string.",
)
def read_doc_contents(
    doc_id: str = Field(description="Id of the document to read"),
) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]


@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing an exact string with a new one.",
)
def edit_document(
    doc_id: str = Field(description="Id of the document to edit"),
    old_str: str = Field(
        description="Text to replace. Must match exactly, including whitespace"
    ),
    new_str: str = Field(description="New text that replaces old_str"),
) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    if old_str not in docs[doc_id]:
        raise ValueError(f"Text {old_str!r} not found in {doc_id}")
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return f"Replaced text in {doc_id}"


@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())


@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]


@mcp.prompt(
    name="format",
    description="Rewrites the contents of a document in Markdown format.",
)
def format_document(
    doc_id: str = Field(description="Id of the document to format"),
) -> list[base.Message]:
    prompt = f"""
Your goal is to reformat a document so it is written in clean Markdown.

The id of the document you need to reformat is:
<document_id>
{doc_id}
</document_id>

Read the document first, then rewrite it using Markdown headings, lists and
emphasis where they help. Keep the meaning unchanged. Use the edit_document
tool to apply the new version. Do not add content that is not in the original.
"""
    return [base.UserMessage(prompt)]


if __name__ == "__main__":
    mcp.run(transport="stdio")
