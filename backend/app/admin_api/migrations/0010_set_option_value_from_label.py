from django.db import migrations


def set_option_value_from_label(apps, schema_editor):
    RecycleQuestionOption = apps.get_model('admin_api', 'RecycleQuestionOption')
    queryset = RecycleQuestionOption.objects.order_by('question_template_id', 'id')

    current_question_id = None
    seen = {}
    for option in queryset:
        if option.question_template_id != current_question_id:
            current_question_id = option.question_template_id
            seen = {}

        base_label = option.label or ''
        seen[base_label] = seen.get(base_label, 0) + 1
        if seen[base_label] == 1:
            new_label = base_label
        else:
            new_label = f"{base_label} ({seen[base_label]})"

        if option.label != new_label or option.value != new_label:
            option.label = new_label
            option.value = new_label
            option.save(update_fields=['label', 'value', 'updated_at'])


class Migration(migrations.Migration):
    dependencies = [
        ('admin_api', '0009_remove_recycle_template_options'),
    ]

    operations = [
        migrations.RunPython(set_option_value_from_label, migrations.RunPython.noop),
    ]
