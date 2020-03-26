class ArticleMapping:

    def __init__(self, article, score):
        self.article = article
        self.score = score

    def confidence_style(self):
        if self.score < 0.5:
            return 'text-warning'
        else:
            return 'text-error'

    def confidence_text(self, language):
        if self.score < 0.5:
            if language == 'sk':
                return 'Môže obsahovať výrok'
            else:
                return 'Might contain claim'
        else:
            if language == 'sk':
                return 'Pravdepodobne obsahuje výrok'
            else:
                return 'Likely contains claim'