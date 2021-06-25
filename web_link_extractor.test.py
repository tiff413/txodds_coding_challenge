import unittest
from web_link_extractor import *

class ProducerLinkExtractor_Test(unittest.TestCase):
    def test1_URL_text_includes_lines(self):
        """Read URLs when they span between different lines"""
        test_str = "youtube.com\ngoogle.com\n\nfacebook.com\n\n\nreddit.com"
        test_correct = ["youtube.com","google.com","facebook.com","reddit.com"]
        self.assertEqual(ProducerLinkExtractor(test_str, []), test_correct)

    def test2_URL_text_includes_commas(self):
        """Replace commas with spaces to get valid URLs"""
        test_str_2 = "youtube.com,google.com,,,,facebook.com, reddit.com"
        test_correct = ["youtube.com","google.com","facebook.com","reddit.com"]
        self.assertEqual(ProducerLinkExtractor(test_str_2, []), test_correct)

    def test3_URL_text_within_sentences(self):
        """Read URLs within a sentence"""
        test_str_3 = "My favourite website is youtube.com and google.com. But I often browse facebook.com and reddit.com too!"
        test_correct = ["youtube.com","google.com","facebook.com","reddit.com"]
        self.assertEqual(ProducerLinkExtractor(test_str_3, []), test_correct)

    def test4_ballooned_queue_size(self):
        """Shrink queue to most recent 50 URLs if more than 50 URLs read"""
        existing_queue = ["reddit.com"]*30
        test_str = """
        google.com,google.com,google.com,google.com,google.com,
        google.com,google.com,google.com,google.com,google.com,
        google.com,google.com,google.com,google.com,google.com,
        google.com,google.com,google.com,google.com,google.com,
        google.com,google.com,google.com,google.com,google.com,
        google.com,google.com,google.com,google.com,google.com,
        """
        queue_correct = (["reddit.com"]*20) + (["google.com"]*30)
        self.assertEqual(ProducerLinkExtractor(test_str, existing_queue), queue_correct)


class ConsumerHyperlinkExtractor_Test(unittest.TestCase):
    def test1_URL_queue_is_empty(self):
        """Return inputted results_dict"""
        results_dict={"existing.com":"result.com"}
        self.assertEqual(ConsumerHyperlinkExtractor([],results_dict), results_dict)

    def test2_URL_queue_pops_first_elem(self):
        """First element from URL queue is popped"""
        url_queue = ["a","b","c"]
        url_queue_correct = ["b", "c"]
        ConsumerHyperlinkExtractor(url_queue)
        self.assertEqual(url_queue, url_queue_correct)


class HyperlinkExtractor_Test(unittest.TestCase):
    def test1_URL_is_invalid(self):
        """Return None, None"""
        correct = None, None
        self.assertEqual(HyperlinkExtractor("not a URL"), correct)

    def test2_URL_has_no_schema(self):
        """Add https:// to front of url"""
        response = requests.get("https://google.com")
        html = response.content
        soup = BeautifulSoup(html, features="lxml")

        # Find all hrefs
        hyperlinks_list = soup.find_all(href=True)
        hyperlinks_list_correct = [line['href'] for line in hyperlinks_list]

        result_correct = "https://google.com", hyperlinks_list_correct
        self.assertEqual(HyperlinkExtractor("google.com"), result_correct)


if __name__ == '__main__':
    unittest.main(verbosity=0, buffer=True)
