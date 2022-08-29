class HtmlProcessPipeline(object):
    """HtmlProcessPipeline"""

    def process_item(self, item, spider):
        """
        process_item
        :param item:
        :param spider:
        :return:
        """
        if item['discussion_html']:
            filename = 'outputs/html/%s.html' % item['discussion_id']
            with open(filename, 'wb') as f:
                f.write(item['discussion_html'])
            del item['discussion_html']

        return item
