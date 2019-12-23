from lib.parser import dom_node, simple_parser


class subscribe_manager():
    def __init__(self, subscriber_config = './config/subscriber.xml'):
        self.subscriber_config = None
        self.subscribers = {}
        if subscriber_config is not None:
            self.subscriber_config  = subscriber_config
            self.load()

    def show(self):
        if self.subscribers is None:
            print('No subscriber found!')
        else:
            for name in self.subscribers:
                print('Name:', name, 'Email:', self.subscribers[name]['email'])

    def load(self, path=None):
        if path is None:
            path = self.subscriber_config
        if path is None:
            return None
        tree = None
        with open(path, 'r') as f:
            xml = f.read()
            parser = simple_parser()
            parser.feed(xml)
            tree = parser.root
        subscribers = {}
        if tree is not None:
            for person in tree.childs:
                person_name = None
                person_email = None
                person_topics = []
                person_keywords = []
                for item in person.childs:
                    if item.name == 'name':
                        person_name = item.data
                    elif item.name == 'email':
                        person_email = item.data
                    elif item.name == 'topics':
                        for topic in item.childs:
                            if topic.name == 'topic':
                                person_topics.append(topic.data)
                    elif item.name == 'keywords':
                        for keyword in item.childs:
                            if keyword.name == 'keyword':
                                person_keywords.append(keyword.data)
                if person_name is not None and person_email is not None and person_topics is not None:
                    subscriber = {}
                    subscriber['keywords'] = person_keywords
                    subscriber['email'] = person_email
                    subscriber['topics'] = person_topics
                    subscribers[person_name] = subscriber
        self.subscribers = subscribers
        print('Subscriber load success! All subscribers are shown below:')
        self.show();

    def get_subscribed_topics(self):
        topics = []
        for name in self.subscribers:
            subscriber = self.subscribers[name]
            topics += subscriber['topics']
        topics = set(topics)
        return topics

    def get_subscribed_keywords(self):
        keywords = []
        for name in self.subscribers:
            keywords += self.subscribers[name]['keywords']
        keywords = set(keywords)
        return keywords

    def get_keywords_of_topics(self):
        keywords_of_topics = {}
        for name in self.subscribers:
            subscriber = self.subscribers[name]
            topic_group = subscriber['topics']
            for topic in topic_group:
                if topic not in keywords_of_topics:
                    keywords_of_topics[topic] = []
                keywords_of_topics[topic] += subscriber['keywords']
        return keywords_of_topics


if __name__ == '__main__':
    manager = subscribe_manager()
    print(manager.subscribers)
    print(manager.get_subscribed_topics())
    print(manager.get_subscribed_keywords())
    print(manager.get_keywords_of_topics())