def validasi_mata_kuliah(
    kode,
    nama,
    sks,
    dosen,
    enroll_code
):

    if not kode.strip():
        return False, "Kode mata kuliah wajib diisi"

    if not nama.strip():
        return False, "Nama mata kuliah wajib diisi"

    if sks < 1:
        return False, "SKS tidak valid"

    if not dosen.strip():
        return False, "Nama dosen wajib diisi"

    if not enroll_code.strip():
        return False, "Kode join wajib diisi"

    return True, ""