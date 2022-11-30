import json
from formtools.wizard.views import SessionWizardView


class MySessionWizardView(SessionWizardView):
    latest_page: str = '0'
    revealed_page: list = []

    def get_form_kwargs(self, step=None):
        form_kwargs = super().get_form_kwargs(step)
        if step is None: step = self.steps.current
        self.update_latest_page(step)
        self.update_revealed_page(step)
        
        return form_kwargs

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form, **kwargs)
        extra_data = self.storage.extra_data
        
        context['latest_page'] = extra_data.get('latest_page')
        context['revealed_page'] = extra_data.get('revealed_page')
        return context

    def update_latest_page(self, new_page: str):
        # Get latest page from storage
        extra_data = self.storage.extra_data
        self.latest_page = extra_data.get('latest_page')
        # Extra data will be none at the first time
        if self.latest_page is None: 
            # Set default value
            self.latest_page = '0'
        # Return if new page is smaller than latest page
        if int(new_page) < int(self.latest_page): return

        # Update latest page
        self.latest_page = new_page
        self.storage.extra_data.update({'latest_page': self.latest_page})

    def update_revealed_page(self, new_page: str):
        # Get latest page from storage
        extra_data = self.storage.extra_data
        revealed_page = extra_data.get('revealed_page')
        # Extra data will be none at the first time
        if revealed_page is None:
            # Set default value
            self.revealed_page = []
        else:
            # Load JSON value if there is extra data
            self.revealed_page = json.loads(revealed_page)
        # Return if new page is already in revealed page
        if new_page in self.revealed_page: return
        
        # Update revealed page
        self.revealed_page.append(new_page)
        self.storage.extra_data.update({'revealed_page': json.dumps(self.revealed_page)})
