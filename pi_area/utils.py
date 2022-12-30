from kurikulum.models import Kurikulum
from ilo.models import Ilo
from .models import (
    AssessmentArea,
    PerformanceIndicatorArea,
    PerformanceIndicator
)


def get_kurikulum_with_pi_area(kurikulum_obj: Kurikulum):
    kurikulum_choices = []

    # Get list kurikulum and exclude obj itself
    kurikulum_qs = Kurikulum.objects.filter(
        prodi=kurikulum_obj.prodi.id_neosia).exclude(id_neosia=kurikulum_obj.id_neosia)

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
    assessment_area_qs = AssessmentArea.objects.filter(
        kurikulum=kurikulum_id
    )

    # Duplicate assessment area
    for assessment_area_obj in assessment_area_qs:
        pi_area_qs = PerformanceIndicatorArea.objects.filter(
            assessment_area=assessment_area_obj,
            assessment_area__kurikulum=kurikulum_id,
        )

        new_assessment_area_obj = assessment_area_obj
        new_assessment_area_obj._state.adding = True
        new_assessment_area_obj.pk = None
        new_assessment_area_obj.kurikulum = new_kurikulum
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

            new_pi_area_obj = pi_area_obj
            new_pi_area_obj._state.adding = True
            new_pi_area_obj.pk = None
            new_pi_area_obj.assessment_area = new_assessment_area_obj
            new_pi_area_obj.save()

            # Duplicate Performance Indicator
            for pi_obj in pi_qs:
                new_pi_obj = pi_obj
                new_pi_obj._state.adding = True
                new_pi_obj.pk = None
                new_pi_obj.pi_area = new_pi_area_obj
                new_pi_obj.save()

            # Duplicate ILO
            for ilo_obj in ilo_qs:
                new_ilo_obj = ilo_obj
                new_ilo_obj._state.adding = True
                new_ilo_obj.pk = None
                new_ilo_obj.pi_area = new_pi_area_obj
                new_ilo_obj.persentase_capaian_ilo = 0
                new_ilo_obj.save()
