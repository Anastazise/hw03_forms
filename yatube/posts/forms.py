from django import forms
from .models import Post

MIN_POST_LEN = 2


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ("text", "group")
        help_texts = {
            'text':('Текст поста'),
            'group':('К какой группе принадлежит'),
        }

    def clean_text(self):
        data = self.cleaned_data["text"]

        if len(data) < MIN_POST_LEN:
            raise forms.ValidationError(
                f"Длинна поста должна быть не менее {MIN_POST_LEN} символов!"
            )

        return data
