class GDPR:
    # Contains the GDPR, where individual statements are represented as list of Rules.
    # The rules are organized by articles, paragraphs, lists, and points
    def __init__(self) -> None:
        self.articles = {}
    
    def add_article(self, article):
        if article not in self.articles:
            self.articles[article] = {"statements": []}
    
    def add_paragraph(self, article, paragraph):
        if article not in self.articles:
            self.add_article(article)
        if paragraph not in self.articles[article]:
            self.articles[article][paragraph] = {"statements": []}
    
    def add_list(self, article, paragraph, list):
        if article not in self.articles or paragraph not in self.articles[article]:
            self.add_paragraph(article, paragraph)
        if list not in self.articles[article][paragraph]:
            self.articles[article][paragraph][list] = {"statements": []}
    
    def add_list_point(self, article, paragraph, list, point):
        if article not in self.articles or paragraph not in self.articles[article] or list not in self.articles[article][paragraph]:
            self.add_list(article, paragraph, list)
        if point not in self.articles[article][paragraph][list]:
            self.articles[article][paragraph][list][point] = {"statements": []}
    
    
    
    def add_statement(self, article: str, paragraph: str, list: str, point: str, statement: list):
        if point is None or list is None:
            self.articles[article][paragraph]["statements"].append(statement)
        else:
            self.articles[article][paragraph][list][point]["statements"].append(statement)
                
    def get_articles(self):
        return self.articles
    
