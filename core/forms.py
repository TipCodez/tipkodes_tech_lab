from django import forms

from .models import BlogComment, ContactMessage, NewsletterSubscription


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "subject": forms.TextInput(attrs={"placeholder": "How can I help?"}),
            "message": forms.Textarea(attrs={"rows": 6, "placeholder": "Write your message..."}),
        }

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 10:
            raise forms.ValidationError("Please enter at least 10 characters.")
        return message


class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ["name", "email", "comment"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "comment": forms.Textarea(attrs={"rows": 5, "placeholder": "Share a thoughtful comment..."}),
        }

    def clean_comment(self):
        comment = self.cleaned_data["comment"].strip()
        if len(comment) < 10:
            raise forms.ValidationError("Please enter at least 10 characters.")
        return comment


class NewsletterSubscriptionForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ["name", "email"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
        }


class CertificateVerificationForm(forms.Form):
    credential_id = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "Enter credential ID"}),
    )
