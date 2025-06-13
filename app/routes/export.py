from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Category, CategoryAttribute, Follow, Item
from app import db
from flask import make_response, render_template
from xhtml2pdf import pisa
import io

export_ns = Namespace('export', description='export related operations')

def get_attr_name(field_id):
    attr = CategoryAttribute.query.get(field_id)
    return attr.name if attr else 'Unknown'

@export_ns.route('/<int:category_id>')
class ExportResource(Resource):
    @export_ns.doc(description='Export items from a category as a PDF')
    @jwt_required()
    def get(self, category_id):
        user_id = get_jwt_identity()
        category = Category.query.get(category_id)
        items = Item.query.filter_by(owner_id=user_id, category_id=category_id).all()

        if not items:
            return {'message': 'no items found'}, 404

        rendered = render_template(
            'export.html',
            items=items,
            category_id=category_id,
            name = category.name,
            get_attr_name=get_attr_name
        )

        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(rendered, dest=pdf_buffer)

        if pisa_status.err:
            return {'message': 'PDF generation failed'}, 500

        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={category.name}_items.pdf'
        return response