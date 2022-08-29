import requests


class ImagesProcessPipeline(object):
    """ImagesProcessPipeline"""

    def process_item(self, item, spider):
        """
        process item
        :param item:
        :param spider:
        :return:
        """
        if item['images']:
            for index, image in enumerate(item['images']):
                image_file_name = item['question_id'] + '_' + str(index) + '.png'
                image_file = requests.get('https://www.examtopics.com' + image)
                with open(image_file_name, 'wb') as f:
                    f.write(image_file.content)
                item['images'][index] = item['category'] + image

        return item
