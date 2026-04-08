# Hardcoded user registry.
# To generate hashes for new passwords, run: python add_user.py
# Then paste the output line into USERS below.

USERS = {
    # "username": "werkzeug-hash"
    # Paste generated hashes here, e.g.:
    "mebertk9": "scrypt:32768:8:1$qqZwD2hbzMk7sKSS$c2a03b620df892fa919d7be83c3f01e677c6e6017b2a68f7a676c947822b2e68154823e1b2612215f46c3b85733183e302872e9697feeabb236c22846ddddaae",
    "Maxi": "scrypt:32768:8:1$Q6y4y6JdLNiUiBHX$ade0f3b381b4393adc155c8020c265880c4bbc680345ca9534bd051579684991c5ed0ce77dd4a5430d097d86b742ef4dc725aee4aaeb1e39e70577b3613112d8",
    "Dennis": "scrypt:32768:8:1$oPYbUmcsPcMp898f$a3eacc0cc0ba351e8169bb59d8057e24bbfcd7f06649923ee8a66c446d3ab5eb2b36daaa727126bd90c323b6f64c59c63813201d0350a7b683a74944c4f0b862",
    "Sassi": "scrypt:32768:8:1$wXmfgpRowq4LPX9x$f3e6757da3bf011171192e79ee7a2165afc3a3a090dfe97307938ad89295c435e45b8d17d897c08cc90bae8840de96724cee8127fbbce3e29bab272abd813f2d",
    "Nils": "scrypt:32768:8:1$xSxMnHv2qIJ5Raxg$a7cef645bf3e77bb7d0cb54bae740f58c79311c8f83e400879fcde22b4fc233cc10cc5d078292fc6cb592f42e0b0b3c740924b5ca688e43a3bd3ce8557f42b55",
}

# Only this user sees the lock icon (finalize game).
# No backend enforcement — by design.
ADMIN_USER = "mebertk9"