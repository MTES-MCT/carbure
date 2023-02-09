from core.traceability import Node


def group_nodes_by_type(nodes):
    data = {
        Node.LOT: [],
        Node.STOCK: [],
        Node.STOCK_TRANSFORM: [],
        Node.TICKET_SOURCE: [],
        Node.TICKET: [],
    }

    # get the list of lots modified by this update
    for node in nodes:
        data[node.type].append(node.data)

    return data
