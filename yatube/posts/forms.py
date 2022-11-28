from django import forms
from .models import Post

MIN_POST_LEN = 30


class PostForm(forms.ModelForm):
    """Форма добавления поста."""

    class Meta:
        model = Post
        fields = ("text", "group")

    def clean_text(self):
        data = self.cleaned_data["text"]

        if len(data) < MIN_POST_LEN:
            raise forms.ValidationError(
                f"Длинна поста должна быть не менее {MIN_POST_LEN} символов!"
            )

        return data
