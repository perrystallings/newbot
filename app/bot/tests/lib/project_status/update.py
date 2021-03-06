from django.test import TestCase


class UpdateProjectStatusTestCase(TestCase):
    def setUp(self):
        from bot.lib.maker import create_maker
        from bot.lib.project import create_project, update_project
        from bot.lib.material import create_material
        from bot.lib.pattern import create_pattern
        from bot.lib.project_status import create_project_status
        self.sender_id = '1'
        self.pattern_url = 'http://via.placeholder.com/350x150'
        self.pattern_type = 'image'
        self.material_url = 'http://via.placeholder.com/350x350'
        self.material_type = 'image'
        self.project_name = 'test_project'
        self.due_date = '2017-01-01'
        self.tags = ['1', '2', '3']
        self.update_url = 'http://via.placeholder.com/350x550'
        self.update_type = 'image'
        create_maker(sender_id=self.sender_id)
        project, created = create_project(sender_id=self.sender_id, name=self.project_name)
        self.project = project
        self.material = create_material(sender_id=self.sender_id, url=self.material_url, file_type=self.material_type)
        self.pattern = create_pattern(sender_id=self.sender_id, url=self.pattern_url, file_type=self.pattern_type)
        self.update_url_2 = 'http://via.placeholder.com/350x650'
        update_project(
            sender_id=self.sender_id,
            project_id=str(self.project.id),
            date_string=self.due_date,
            material_id=str(self.material.id),
            pattern_id=str(self.pattern.id),
            tags=self.tags
        )
        self.project_status = create_project_status(
            sender_id=self.sender_id,
            project_id=str(self.project.id),
            url=self.update_url,
            file_type=self.update_type
        )

    def test_add_image(self):
        from bot.lib.project_status import update_project_status
        from bot.models import ProjectStatus
        project_status = update_project_status(
            sender_id=self.sender_id,
            project_status_id=str(self.project_status.id),
            file=dict(
                url=self.update_url_2,
                file_type='image'
            ),

        )
        self.assertFalse(project_status.complete)
        self.assertEqual(ProjectStatus.objects.get(id=project_status.id).files.count(), 2)

    def test_add_tags(self):
        from bot.lib.project_status import update_project_status
        from bot.models import ProjectStatus
        project_status = update_project_status(
            sender_id=self.sender_id,
            project_status_id=str(self.project_status.id),
            tags=self.tags
        )
        self.assertFalse(project_status.complete)
        self.assertEqual(ProjectStatus.objects.get(id=project_status.id).tags.count(), 3)

    def test_add_completion(self):
        from bot.lib.project_status import update_project_status
        from bot.models import ProjectStatus
        project_status = update_project_status(
            sender_id=self.sender_id,
            project_status_id=str(self.project_status.id),
            completion_percentage=80
        )
        self.assertTrue(project_status.complete)
        self.assertEqual(ProjectStatus.objects.get(id=project_status.id).completion.percentage, 80)
