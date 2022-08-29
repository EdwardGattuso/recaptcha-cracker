import uuid

from examtopicscrawler.utils import common


class OptionProcessPipeline(object):
    """OptionProcessPipeline"""

    def process_item(self, item, spider):
        """
        process item
        :param item:
        :param spider:
        :return:
        """
        if item['option_nums']:
            format_option_nums = common.strip_newline_from_list(item['option_nums'])
            del item['option_nums']
            if item['option_items']:
                format_option_items = common.strip_newline_from_list(item['option_items'])
                del item['option_items']
                item['choices'] = [i + j for i, j in zip(format_option_nums, format_option_items)]
            item['question_id'] = str(uuid.uuid1())
        return item
