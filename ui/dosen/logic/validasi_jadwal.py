def validasi_jadwal(
    hari,
    jam_mulai,
    jam_selesai,
    ruangan
):

    if not hari:

        return (
            False,
            "Hari wajib dipilih"
        )

    if jam_mulai >= jam_selesai:

        return (
            False,
            "Jam selesai harus lebih besar dari jam mulai"
        )

    if not ruangan.strip():

        return (
            False,
            "Ruangan wajib diisi"
        )

    return (
        True,
        ""
    )