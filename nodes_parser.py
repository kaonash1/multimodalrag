from llama_index.core import Document
from llama_index.core.schema import TextNode, ImageNode, NodeRelationship, RelatedNodeInfo
from typing import List, Dict, Any

def process_composite_elements(composite_elements: List[Any]) -> List:
    """Process Unstructured CompositeElements into LlamaIndex Nodes with relationships."""
    all_nodes = []
    node_dict = {}  # To track nodes by ID
    
    for composite in composite_elements:
        # Create a parent node for the composite
        parent_id = f"composite_{id(composite)}"
        parent_node = Document(
            text=composite.text,
            id_=parent_id,
            metadata={
                "source": composite.metadata.filename,
                "type": "composite"
            }
        )
        all_nodes.append(parent_node)
        node_dict[parent_id] = parent_node
        

        # Process each element within the composite
        for i, element in enumerate(composite.metadata.orig_elements):
            child_id = f"{parent_id}_element_{i}"
            
            # Create appropriate node based on element type
            if (element.category == "Image") and hasattr(element.metadata, 'image_base64'):
                child_node = ImageNode(
                    image=element.metadata.image_base64,
                    id_=child_id,
                    text=element.text if hasattr(element, 'text') else "",
                    metadata={
                        "source": composite.metadata.filename,
                        "type": "image"}
                )
            elif element.category == "Table":
                child_node = ImageNode(
                    image=element.metadata.image_base64,
                    id_=child_id,
                    text=element.text,
                    metadata={
                        "source": composite.metadata.filename,
                        "type": "table"}
                )
            else:
                child_node = TextNode(
                    text=element.text,
                    id_=child_id,
                    metadata={
                        "source": composite.metadata.filename,
                        "type": "text"}
                )
                
            all_nodes.append(child_node)
            node_dict[child_id] = child_node
            
            # Set up parent-child relationships using RelatedNodeInfo
            parent_node.relationships.setdefault(NodeRelationship.CHILD, []).append(
                RelatedNodeInfo(node_id=child_id)
            )
            child_node.relationships.setdefault(NodeRelationship.PARENT, []).append(
                RelatedNodeInfo(node_id=parent_id)
            )
            
            # Add sibling relationships if needed
            if i > 0:
                prev_id = f"{parent_id}_element_{i-1}"

                node_dict[prev_id].relationships[NodeRelationship.NEXT] = RelatedNodeInfo(node_id=child_id)
                child_node.relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(node_id=prev_id)
        
    #after handling individual composites, set relationships between the composites
    for i in range(1, len(composite_elements)):
        prev_composite_id = f"composite_{id(composite_elements[i-1])}"
        curr_composite_id = f"composite_{id(composite_elements[i])}"
        

        node_dict[prev_composite_id].relationships[NodeRelationship.NEXT] = RelatedNodeInfo(node_id=curr_composite_id)
        node_dict[curr_composite_id].relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(node_id=prev_composite_id)


        
    return all_nodes