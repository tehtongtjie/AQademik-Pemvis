def validasi_materi(
    judul,
    file_path
):

    if not judul.strip():
        return False, "Judul wajib diisi"

    if not file_path:
        return False, "File wajib dipilih"

    return True, ""