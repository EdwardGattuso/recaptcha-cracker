from scrapy.cmdline import execute

import os
import sys

if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    execute("scrapy crawl examtopics -o outputs/examtopics.json -a url=https://www.examtopics.com/exams/amazon/aws-certified-solutions-architect-professional/view/ -a category=AmazonAWSCertifiedSolutionsArchitect".split())