from html.parser import HTMLParser
from . import utils

def dict_to_arrtibute_string(attributes):
    string = ''
    for key in attributes:
        string += key + '=\"{0}\";'.format(str(attributes[key]))
    return string

def attribute_string_to_dict(attrs):
    attr_dict = {}
    for attr in attrs:
        attr_dict[attr[0]] = attr[1]
    return attr_dict


class dom_node():
    def __init__(self, name = None, attributes = {}):
        if name is not None:
            self.name = name
        else:
            self.name = 'Node'

        self.attributes = attributes
        self.childs = []
        self.data = None
        self.father = None

    def add_child(self, child):
        if child is not None:
            child.father = self
            self.childs.append(child)

    def to_string(self, prefix='', indent='    '):

        string = prefix + '<' + self.name
        if self.attributes:
            string += ' ' + dict_to_arrtibute_string(self.attributes)
        string += '>\n'

        for child in self.childs:
            string += child.to_string(prefix=prefix+indent, indent=indent)

        if self.data is not None:
            string += prefix + indent + self.data + '\n'

        string += prefix + '</{0}>\n'.format(self.name)

        return string


    def has_child(self, name):
        has = False
        for child in self.childs:
            if child.name  == name:
                has = True
                break;
        return has

    def search(self, name):
        founded_node = []
        if type(name) is list:
            if self.name in name:
                founded_node.append(self)
        else:
            if self.name == name:
                founded_node.append(self)
        for child in self.childs:
            search_result = child.search(name)
            founded_node += search_result
        return founded_node

def dict2dom(d, root_name='root'):
	node = dom_node(root_name)
	for key in d:
		elem = d[key]
		child_node = dom_node(name=str(key))
		if type(elem) is dict:
			child_node = dict2dom(elem, root_name=str(key))
		elif type(elem) is list:
			for subelem in elem:
				if type(subelem) is dict:
					sub_node = dict2dom(subelem, root_name='li')
					child_node.add_child(sub_node)
				else:
					sub_node = dom_node('li')
					sub_node.data = str(subelem)
					child_node.add_child(sub_node)
		else:
			child_node.data = str(elem)
		node.add_child(child_node)
	return node

# if a dom node has data only, then it's {'name':'data'}
# if a dom node has childs, then it's {'name':{}}
# if a dom node has data as well as childs, data will be ignored.
# if a dom has multi child with same name, it will be stored as list.
def dom2dict(dom, replace_li = True):
	dictionary = {}
	for child in dom.childs:
		name = child.name
		content = None
		if len(child.childs) != 0:
			content = dom2dict(child, replace_li)
		else:
			content = child.data
			if content is None:
				content = ''
			content = utils.clean_text(content)
		if name in dictionary:
			if type(dictionary[name]) is not list:
				previous = dictionary[name]
				dictionary[name] = [previous, content]
			else:
				dictionary[name].append(content)
		else:
			dictionary[name] = content

	if replace_li:
		for key in dictionary:
			item = dictionary[key]
			if type(item) is dict:
				li = None
				if len(item.keys()) == 1:
					for subkey in item:
						if subkey == 'li':
							li = item[subkey]
				if li is not None:
					dictionary[key] = li
	return dictionary

class simple_parser(HTMLParser):
    def __init__(self):
        super(simple_parser, self).__init__()
        self.root = dom_node('root')
        self.current_node = self.root

    def handle_starttag(self, tag, attrs):
        attrs_dict = attribute_string_to_dict(attrs)
        this_node = dom_node(tag, attrs_dict)
        self.current_node.add_child(this_node)
        self.current_node = this_node

    def handle_endtag(self, tag):
        self.current_node = self.current_node.father

    def handle_data(self, data):
        if self.current_node.data is None:
            self.current_node.data = data
        else:
            self.current_node.data += data