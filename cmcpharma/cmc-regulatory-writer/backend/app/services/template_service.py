from ..models.template import Template, TemplateCreationRequest, TOCItem
from ..utils.parsers import parse_toc_from_text

class TemplateService:
    def create_template_from_text(self, request: TemplateCreationRequest) -> Template:
        """
        Creates a structured Template object from a raw text request.
        """
        parsed_toc = parse_toc_from_text(request.toc_text)
        
        new_template = Template(
            name=request.name,
            description=request.description,
            toc=parsed_toc
        )
        return new_template
