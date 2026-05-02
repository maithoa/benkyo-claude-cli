from mcp.server.fastmcp.prompts import base
from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}


@mcp.tool(
    name="read_doc_contents",
    description="Reads the contents of a document given its name and return it as a string.",
)

def read_document(
    doc_id: str = Field(description= "Id of the document to read")
): 
    if doc_id not in docs:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    return docs[doc_id]


@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string in the documents content with another string."
)
def edit_document(
    doc_id: str = Field(description= "Id of the document to edit"),
    old_str: str = Field(description= "String to be replaced in the document. Must match exactly with the string in the document including spaces."),
    new_str : str = Field(description= "The new text to be inserted in place of the old text")
):
    if doc_id not in docs:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    
    if old_str not in docs[doc_id]:
        raise ValueError(f"Target string '{old_str}' not found in document '{doc_id}'.")
    
    docs[doc_id] = docs[doc_id].replace(old_str, new_str)
    return f"Document '{doc_id}' has been updated."

@mcp.resource(
    "docs://documents",
    mime_type="application/json"
)
def list_docs() -> list[str]:
    return list(docs.keys())

@mcp.resource(
    "docs://documents/{doc_id}",
    mime_type="text/plain"
)
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document with id '{doc_id}' not found.")
    return docs[doc_id]

@mcp.prompt(
    name = "format",
    description = "Rewrites the contents of a document in Markdown format.",
)
def format_document(
    doc_id: str=Field(description="Id of the document to format")
) -> list[base.Message]:
    #Return a list of messages
    prompt = f""" 
    Your goal is to reformat a document to be written with markedown syntax. 
    
    The id of the document you need to reformat is 
    <document_id>{doc_id}</document_id>.
    
    Add in headers, bullet points, tables, etc as necessary. 
    Feel free to add in extra formatting . Use the 'edit_document' tool to edit the document. 
    After the document has been reformatted, return the final contents of the document as a message with the role 'final_output' and the content being the reformatted document."""

    return [base.UserMessage(content=prompt)]



# TODO: Write a prompt to summarize a doc


if __name__ == "__main__":
    mcp.run(transport="stdio")
