# Generated by Django 5.1.3 on 2024-12-07 08:57

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('type', models.CharField(choices=[('administrative', 'Administrative'), ('financial', 'Financial'), ('HR', 'Human Resource'), ('marketing_and_sales', 'Marketing and Sales'), ('it_and_technical', 'IT and Technical'), ('operations', 'Operations'), ('strategic', 'Strategic')], max_length=27)),
                ('status', models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('terminated', 'Terminated'), ('waiting_for_approval', 'Waiting For Approval'), ('completed', 'Completed'), ('closed', 'Closed')], default='not_started', max_length=27)),
                ('priority', models.CharField(choices=[('critical', 'Critical'), ('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], max_length=27)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('due_date', models.DateField(default=django.utils.timezone.now)),
                ('all_submitted', models.BooleanField(default=False)),
                ('submitted_date', models.DateTimeField(blank=True, null=True)),
                ('approval_status', models.BooleanField(default=False)),
                ('assigned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('assigned_to', models.ManyToManyField(blank=True, related_name='AssignedUsers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('can_view_approved_tasks', 'Can View Approved Tasks'), ('can_view_submitted_tasks', 'Can View Submitted Tasks')],
            },
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='tasks.task')),
            ],
        ),
        migrations.CreateModel(
            name='TaskSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted', models.BooleanField(default=False)),
                ('submitted_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='tasks.task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
