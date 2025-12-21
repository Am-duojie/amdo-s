from django.core.management.base import BaseCommand
from django.db import transaction

from app.secondhand_app.models import Category, Product, VerifiedProduct


class Command(BaseCommand):
    help = "Merge multiple categories into a target category"

    def add_arguments(self, parser):
        parser.add_argument(
            '--target',
            default='电脑',
            help='Target category name (default: 电脑)',
        )
        parser.add_argument(
            '--sources',
            nargs='+',
            default=['笔记本电脑', '台式电脑'],
            help='Source category names to merge',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show changes without writing to the database',
        )

    def handle(self, *args, **options):
        target_name = options['target'].strip()
        source_names = [name.strip() for name in options['sources'] if name.strip()]
        dry_run = options['dry_run']

        if not source_names:
            self.stderr.write('No source categories provided.')
            return

        sources = list(Category.objects.filter(name__in=source_names))
        if not sources:
            self.stderr.write('No matching source categories found.')
            return

        target = Category.objects.filter(name=target_name).first()
        if not target:
            base = sources[0]
            target = Category(
                name=target_name,
                description=base.description or '电脑类商品',
                type=base.type,
            )
            if not dry_run:
                target.save()

        source_ids = [c.id for c in sources if c.name != target.name]
        if not source_ids:
            self.stdout.write('Nothing to merge.')
            return

        with transaction.atomic():
            products_qs = Product.objects.filter(category_id__in=source_ids)
            verified_qs = VerifiedProduct.objects.filter(category_id__in=source_ids)
            product_count = products_qs.count()
            verified_count = verified_qs.count()

            if not dry_run:
                products_qs.update(category=target)
                verified_qs.update(category=target)
                Category.objects.filter(id__in=source_ids).delete()

        self.stdout.write(
            f"Merged {product_count} products and {verified_count} verified products into '{target.name}'."
        )
        if dry_run:
            self.stdout.write('Dry-run only; no changes were written.')
