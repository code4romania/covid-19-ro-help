from xml.dom.minidom import parse


def load_from_xml():
    f = open("/Users/0dmg/Desktop/Git/NETOPIA/python/request.xml", 'r')
    doc = parse(f)
    f.close()
    return doc


def save_to_xml(root_node, file_path):
    f = open(file_path, "w")
    root_node.writexml(f)
    f.close()
