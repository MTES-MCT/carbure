from core.traceability import LotNode, StockNode, StockTransformNode, TicketSourceNode, TicketNode


def group_nodes_by_model(nodes):
    data = {
        "lots": [],
        "stocks": [],
        "stock_transforms": [],
        "ticket_sources": [],
        "tickets": [],
    }

    # get the list of lots modified by this update
    for node in nodes:
        if isinstance(node, LotNode):
            data["lots"].append(node.data)
        if isinstance(node, StockNode):
            data["stocks"].append(node.data)
        if isinstance(node, StockTransformNode):
            data["stock_transforms"].append(node.data)
        if isinstance(node, TicketSourceNode):
            data["ticket_sources"].append(node.data)
        if isinstance(node, TicketNode):
            data["tickets"].append(node.data)

    return data
