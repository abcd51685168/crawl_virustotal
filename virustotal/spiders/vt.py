__author__ = 'lunac'

import scrapy
import json


class VtSpider(scrapy.Spider):
    name = "vt"
    allowed_domains = ["virustotal.com"]
    start_urls = [
        "https://www.virustotal.com/en/file/4ee9e741d65680cd4c44b5e9a5d7636511c0ae4b3e774b454b17fdc675edf289/analysis/"
    ]

    def parse(self, response):
        def get_real_value(values_list):
            return [i.strip() for i in values_list if i.strip()][0]

        # print response.body
        result = {}
        for h5 in response.xpath('//h5'):
            h5_text = h5.xpath('text()').extract()[0].strip()
            print h5_text

        for field in response.xpath('//div[@class="enum-container"]'):
            preceding_field = field.xpath('preceding-sibling::*[1]')
            h5 = preceding_field.xpath('text()').extract()[0].strip()
            if h5 in ["Packers identified", "PE header basic information", "Number of PE resources by type",
                      "Number of PE resources by language", ]:
                content = {}
                for filed_enum in field.xpath('div[@class="enum"]'):
                    field_key = filed_enum.xpath('span[@class="field-key"]/text()').extract()[0].strip()
                    field_value = get_real_value(filed_enum.xpath('text()').extract())
                    # field_value = [i.strip() for i in filed_enum.xpath('text()').extract() if i.strip()][0]
                    # print field_key, field_value
                    content[field_key] = field_value

                result[h5] = content

            elif h5 == "PE imports":
                content = {}
                for expand in field.xpath('div[@class="expand-canvas"]'):
                    canvas_key = expand.xpath('div[@class="enum"]/a[@class="expand-data"]/text()').extract()[0].split()[1]
                    canvas_values = [value.xpath('text()').extract()[0].strip() for value in expand.xpath('div[@class="hide"]/div[@class="enum"]')]
                    content[canvas_key] = canvas_values

                result[h5] = content

            elif h5 == "ExifTool file metadata":
                content = {}
                for expand in field.xpath('div[@class="enum"]'):
                    field_key = expand.xpath('div[@class="floated-field-key"]/text()').extract()[0].strip()
                    field_value = expand.xpath('div[@class="floated-field-value"]/text()').extract()[0].strip()
                    content[field_key] = field_value

                result[h5] = content

        for field in response.xpath('//div[@class="enum-container expandable"]'):
            preceding_field = field.xpath('preceding-sibling::*[1]')
            h5 = preceding_field.xpath('text()').extract()[0].strip()
            if h5 == "PE sections":
                content = []
                span_keys = [span.xpath('text()').extract()[0].strip() for span in field.xpath('div[@class="enum text-bold"]/span')]
                for enum in field.xpath('div[@class="enum"]'):
                    span_values = []
                    for span in enum.xpath('span'):
                        span_values.append(get_real_value(span.xpath('text()').extract()))
                    content.append(dict(zip(span_keys, span_values)))

                result[h5] = content

            if h5 in ["Opened files", "Read files", "Opened mutexes", "Runtime DLLs", "UDP communications"]:
                content = []
                for filed_enum in field.xpath('div[@class="enum"]'):
                    content.append(get_real_value(filed_enum.xpath('text()').extract()))

                result[h5] = content

        with open("/tmp/vt.json", 'w') as f:
            json.dump(result, f, indent=4, encoding="utf-8")
