from otree.api import *
from . import C
from . import *


class PlayerBot(Bot):

    def play_round(self):

        yield Welcome
        yield EncryptionTask
        yield Instructions

        # --- Comprehension check: answer correctly depending on treatment ---
        if self.player.treatment:
            yield ComprehensionCheck, dict(
                q1=C.SOLUTIONS['q1'],
                q2=C.SOLUTIONS['q2'],
                q3=C.SOLUTIONS['q3'],
                q4t=C.SOLUTIONS['q4t'],
                q5t=C.SOLUTIONS['q5t'],
            )
        else:
            yield ComprehensionCheck, dict(
                q1=C.SOLUTIONS['q1'],
                q2=C.SOLUTIONS['q2'],
                q3=C.SOLUTIONS['q3'],
                q4c=C.SOLUTIONS['q4c'],
                q5c=C.SOLUTIONS['q5c'],
            )

        # consent yes
        yield Consent, dict(consent=True)

        # NoConsent page is only shown if consent=False, so bot ends here.
