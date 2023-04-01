from kurikulum.models import Kurikulum
from ilo.models import Ilo
from .models import (
    AssessmentArea,
    PerformanceIndicatorArea,
)
from learning_outcomes_assessment.utils import clone_object


def get_kurikulum_with_pi_area(kurikulum_obj: Kurikulum):
    kurikulum_choices = []

    # Get list kurikulum and exclude obj itself
    kurikulum_qs = Kurikulum.objects.filter(
        prodi_jenjang=kurikulum_obj.prodi_jenjang.id_neosia).exclude(id_neosia=kurikulum_obj.id_neosia)

    # Filter Assessment Area and PI Area in the semester
    for kurikulum_obj in kurikulum_qs:
        # Check assessment area
        assessment_area_qs = AssessmentArea.objects.filter(
            kurikulum=kurikulum_obj
        )

        if not assessment_area_qs.exists(): continue

        # Check PI Area
        pi_area_qs = PerformanceIndicatorArea.objects.filter(
            assessment_area__kurikulum=kurikulum_obj
        )

        if not pi_area_qs.exists(): continue

        kurikulum_choices.append(
            (kurikulum_obj.id_neosia, kurikulum_obj.nama)
        )

    return kurikulum_choices


def duplicate_pi_area_from_kurikulum_id(kurikulum_id: int, new_kurikulum: Kurikulum):
    is_success = False
    message = ''

    assessment_area_qs = AssessmentArea.objects.filter(
        kurikulum=kurikulum_id
    )
    cloned_list_assessment_area = []

    # Duplicate assessment area
    for assessment_area_obj in assessment_area_qs:
        new_assessment_area_obj = clone_object(
            assessment_area_obj,
            attrs={
                'kurikulum': new_kurikulum
            }
        )
        cloned_list_assessment_area.append(new_assessment_area_obj)
    
    if assessment_area_qs.count() == len(cloned_list_assessment_area):
        is_success = True
        message = 'Berhasil menduplikasi Assessment Area.'
    else:
        message = 'Jumlah assessment area yang diduplikasi hanya {} area. Ekspektasi: {}.'.format(len(cloned_list_assessment_area), assessment_area_qs.count())

    return (is_success, message)
