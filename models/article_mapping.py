class ArticleMapping:

    def __init__(self, article, score):
        self.article = article
        self.score = score

    def confidence_style(self):
        if self.score < 0.5:
            return 'text-warning'
        else:
            return 'text-error'

    def confidence_text(self):
        if self.score < 0.5:
            return 'Might contain claim'
        else:
            return 'Likely contains claim'