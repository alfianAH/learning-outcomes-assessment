from semester.models import SemesterKurikulum
from .models import (
    AssessmentArea,
    PerformanceIndicatorArea,
    PerformanceIndicator
)


def get_semester_with_pi_area_by_kurikulum(semester_obj: SemesterKurikulum):
    semester_choices = []

    # Get list semester by kurikulum
    semester_kurikulum_qs = SemesterKurikulum.objects.filter(
        kurikulum=semester_obj.kurikulum.id_neosia).exclude(id=semester_obj.pk)

    # Filter Assessment Area and PI Area in the semester
    for semester_kurikulum_obj in semester_kurikulum_qs:
        # Check assessment area
        assessment_area_qs = AssessmentArea.objects.filter(
            semester=semester_kurikulum_obj
        )

        if not assessment_area_qs.exists(): continue

        # Check PI Area
        pi_area_qs = PerformanceIndicatorArea.objects.filter(
            assessment_area__semester=semester_kurikulum_obj
        )

        if not pi_area_qs.exists(): continue

        semester_choices.append(
            (semester_kurikulum_obj.pk, semester_kurikulum_obj.semester.nama)
        )

    return semester_choices


def duplicate_pi_area_from_semester_id(semester_id: int, new_semester: SemesterKurikulum):
    assessment_area_qs = AssessmentArea.objects.filter(
        semester=semester_id
    )

    # Duplicate assessment area
    for assessment_area_obj in assessment_area_qs:
        # Duplicate PI Area 
        pi_area_qs = PerformanceIndicatorArea.objects.filter(
            assessment_area=assessment_area_obj,
            assessment_area__semester=semester_id,
        )

        new_assessment_area_obj = assessment_area_obj
        new_assessment_area_obj._state.adding = True
        new_assessment_area_obj.pk = None
        new_assessment_area_obj.semester = new_semester
        new_assessment_area_obj.save()

        for pi_area_obj in pi_area_qs:
            # Duplicate Performance Indicator
            pi_qs = PerformanceIndicator.objects.filter(
                pi_area=pi_area_obj,
                pi_area__assessment_area__semester=semester_id,
            )

            new_pi_area_obj = pi_area_obj
            new_pi_area_obj._state.adding = True
            new_pi_area_obj.pk = None
            new_pi_area_obj.assessment_area = new_assessment_area_obj
            new_pi_area_obj.save()

            for pi_obj in pi_qs:
                new_pi_obj = pi_obj
                new_pi_obj._state.adding = True
                new_pi_obj.pk = None
                new_pi_obj.pi_area = new_pi_area_obj
                new_pi_obj.save()
