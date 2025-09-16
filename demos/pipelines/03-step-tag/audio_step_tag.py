from markupsafe import Markup
from step import StepTag


class AudioStepTag(StepTag):
    @classmethod
    def get_jinja_translations(cls):
        return {
            "title_frozen": "Completed tags:",
            "title_unfrozen": "Rate existing tags",
            "type_more": "Type more tags",
            "title_tags": "Add tags",
            "next": "Next",
            "instructions_without_tags": Markup(
                """
                <h3>How to add tags?</h3>
                <div class="alert alert-primary" role="alert">
                    Nobody has added tags for this song yet. Add emotion tags you think the song expresses.
                    Keep tags short (single words). Add multiple tags by submitting each one separately (press <kbd>enter</kbd>).
                </div>
                """
            ),
            "instructions_with_tags": Markup(
                """
                <h3>Can you add more tags?</h3>
                <div class="alert alert-primary" role="alert">
                    Others may have already added tags; rate them and add more emotion tags you think the song expresses.
                    Keep tags short (single words). Add multiple tags by submitting each one separately (press <kbd>enter</kbd>).
                </div>
                """
            ),
        }

    @classmethod
    def get_javascript_translations(cls):
        return {
            "translations": {
                "tag_value_exists": "This tag is already in the list.",
                "tag_value_empty": "Type a word before adding a tag.",
            }
        }
