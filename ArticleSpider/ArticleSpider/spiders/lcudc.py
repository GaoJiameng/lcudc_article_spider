# -*- coding: utf-8 -*-
import re
import scrapy

from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import LcudcArticleItem
from ArticleSpider.utils.common import get_md5


class LcudcSpider(scrapy.Spider):
    name = 'lcudc'
    allowed_domains = ['news.lcudcc.edu.cn']
    start_urls = ['http://news.lcudcc.edu.cn/zhxw/301.htm']

    def parse(self, response):
        """
        1. 获取文章列表页中的文章url并交给scrapy下载后并进行解析
        2. 获取下一页的url并交给scrapy进行下载， 下载完成后交给parse
        """

        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        if response.status == 404:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")
        post_nodes = response.css(".xinw958 .xinwim241 a")
        for post_node in post_nodes:
            ex_image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            image_url = "http://news.lcudcc.edu.cn" + ex_image_url
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url":image_url}, callback=self.parse_detail)


        # 提取下一页并交给scrapy进行下载
            ex_next_url = response.css(".Next::attr(href)").extract_first("")
            next_url = "http://news.lcudcc.edu.cn/zhxw/" + ex_next_url
            if next_url:
                yield Request(url=next_url, callback=self.parse)



            # content_src = "http://news.lcudcc.edu.cn/" + response.css(".img_vsb_content::attr(src)").extract_first("")
            # content_vurl = "http://news.lcudcc.edu.cn/" + response.css(".img_vsb_content::attr(vurl)").extract_first("")
            # content_orisrc = "http://news.lcudcc.edu.cn/" + response.css(".img_vsb_content::attr(orisrc)").extract_first("")
            # if content_src:
            #     yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse)




    def parse_detail(self, response):
        article_item = LcudcArticleItem()
        # 提取文章的具体字段
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        title = response.xpath("/html/body/div[3]/div[1]/form/div[1]/text()").extract()[0].strip()
        create_date0 = response.xpath("/html/body/div[3]/div[1]/form/div[2]/text()").extract()[0].strip().replace("\r\n", "")
        match_re = re.match(".*?(2.*)", create_date0)
        if match_re:
            create_date = match_re.group(1)
        content = response.xpath("//*[@id='vsb_content_4']").extract()

        article_item["url_object_id"] = get_md5(response.url)
        article_item["title"] = title
        article_item["url"] = response.url
        article_item["create_date"] = create_date
        article_item["front_image_url"] = [front_image_url]
        article_item["content"] = content

        # 通过item loader加载item
        # front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        # item_loader = ArticleItemLoader(item=LcudcArticleItem(), response=response)
        # item_loader.add_css("title", ".entry-header h1::text")
        # item_loader.add_value("url", response.url)
        # item_loader.add_value("url_object_id", get_md5(response.url))
        # item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        # item_loader.add_value("front_image_url", [front_image_url])
        # item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        # item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        # item_loader.add_css("fav_nums", ".bookmark-btn::text")
        # item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        # item_loader.add_css("content", "div.entry")
        #
        # article_item = item_loader.load_item()



        yield article_item
