def extract_summary(response, first_para_extractor):
	child_int = 1
	while True:
		first_para_text = "" + first_para_extractor + " p:nth-of-type("+ str(child_int) + ") *::text"
		first_paragraph = ''.join(response.css(first_para_text).extract())
		if len(first_paragraph) > 7:
			return first_paragraph
		child_int = child_int + 1
		if child_int > 10:
			return None

def get_url_attributes(source_url, splitter, page_number_joiner=''):
	splitted_url = str(source_url).split(splitter)
	if len(splitted_url) > 1:
		for char in splitted_url[len(splitted_url)-1]:
			if char.isdigit():
				page_number = int(char)+1
	else:
		page_number = 2
	if page_number > 2:
		splitted_url[0] = splitted_url[0] + page_number_joiner
	return {'core_url' : splitted_url[0], 'page_number' : str(page_number)}