from copy import copy
from kurikulum.models import Kurikulum
from ilo.models import Ilo
from .models import (
    AssessmentArea,
    PerformanceIndicator,
    PerformanceIndicatorArea,
)


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

    def duplicate_pi_area_children(list_obj, new_pi_area):
        for obj in list_obj:
            new_obj = copy(obj)
            new_obj._state.adding = True
            new_obj.pk = None
            new_obj.pi_area = new_pi_area
            new_obj.lock = None
            new_obj.save()

    # Duplicate assessment area
    for assessment_area_obj in assessment_area_qs:
        pi_area_qs = PerformanceIndicatorArea.objects.filter(
            assessment_area=assessment_area_obj,
            assessment_area__kurikulum=kurikulum_id,
        )

        new_assessment_area_obj = copy(assessment_area_obj)
        new_assessment_area_obj._state.adding = True
        new_assessment_area_obj.pk = None
        new_assessment_area_obj.kurikulum = new_kurikulum
        new_assessment_area_obj.lock = None
        new_assessment_area_obj.save()
        
        # Duplicate PI Area 
        for pi_area_obj in pi_area_qs:
            pi_qs = PerformanceIndicator.objects.filter(
                pi_area=pi_area_obj,
                pi_area__assessment_area__kurikulum=kurikulum_id,
            )
            ilo_qs = Ilo.objects.filter(
                pi_area=pi_area_obj,
                pi_area__assessment_area__kurikulum=kurikulum_id,
            )

            new_pi_area_obj = copy(pi_area_obj)
            new_pi_area_obj._state.adding = True
            new_pi_area_obj.pk = None
            new_pi_area_obj.assessment_area = new_assessment_area_obj
            new_pi_area_obj.lock = None
            new_pi_area_obj.save()

            # Duplicate PI Area and Performance Indicator
            duplicate_pi_area_children(pi_qs, new_pi_area_obj)
            duplicate_pi_area_children(ilo_qs, new_pi_area_obj)
    
    is_success = True
    message = 'Berhasil menduplikasi Assessment Area.'

    return (is_success, message)
