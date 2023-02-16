import random
import sys
from django.test import TestCase
from .utils import generate_nilai_clo


# Create your tests here.
class CloTestCase(TestCase):
    def test_generate_nilai_clo(self):
        for i in range(1000):
            nilai_akhir = random.random() * 100

            sys.stdout.write("\rPercobaan: {} Nilai akhir: {}".format(i, nilai_akhir))

            list_persentase_komponen_clo_len = random.randint(1, 10)
            list_persentase_komponen_clo = []

            for j in range(list_persentase_komponen_clo_len):
                if j == list_persentase_komponen_clo_len-1:
                    persentase = 100 - sum(list_persentase_komponen_clo)
                else:
                    persentase = random.randrange(1, int(100/list_persentase_komponen_clo_len))
                
                list_persentase_komponen_clo.append(persentase)
            
            self.assertEqual(sum(list_persentase_komponen_clo), 100)

            generated_nilai_peserta = generate_nilai_clo(list_persentase_komponen_clo, nilai_akhir)
            generated_nilai_akhir = 0

            for i, persentase_komponen_clo in enumerate(list_persentase_komponen_clo):
                generated_nilai_akhir += persentase_komponen_clo/100 * generated_nilai_peserta[i] 

            self.assertAlmostEqual(generated_nilai_akhir, nilai_akhir, delta=1)
