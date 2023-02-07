from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': 'Напишите что-нибудь, но избегайте слова "ёж".',
        }

    def clean_text(self):
        data = self.cleaned_data['text']
        if 'ёж' in data.lower():
            raise forms.ValidationError('Слово ёж под запретом!')
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Напишите какой-нибудь комментарий к публикации.',
        }
