from kurikulum.models import Kurikulum
from pi_area.models import (
    PerformanceIndicatorArea,
    PerformanceIndicator
)


def get_pi_area_by_kurikulum_choices(kurikulum_obj: Kurikulum):
    pi_area_qs = PerformanceIndicatorArea.objects.filter(assessment_area__kurikulum=kurikulum_obj)
    pi_area_choices = []

    for pi_area in pi_area_qs:
        if pi_area.ilo is None:
            pi_area_choice = pi_area.pk, pi_area.pi_code
        else:
            pi_area_choice = pi_area.pk, '{} - {}'.format(pi_area.pi_code, pi_area.ilo.nama)

        pi_area_choices.append(pi_area_choice)

    return pi_area_choices


def get_pi_by_pi_area_choices(pi_area_id):
    pi_qs = PerformanceIndicator.objects.filter(pi_area__id=pi_area_id)
    pi_choices = []

    for pi in pi_qs:
        pi_choice = pi.pk, pi.deskripsi

        pi_choices.append(pi_choice)
    
    return pi_choices
