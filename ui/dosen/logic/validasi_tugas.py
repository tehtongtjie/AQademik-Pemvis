def validasi_tugas(
    judul,
    deskripsi
):

    if not judul.strip():
        return False, "Judul tugas wajib diisi"

    if not deskripsi.strip():
        return False, "Deskripsi tugas wajib diisi"

    return True, ""