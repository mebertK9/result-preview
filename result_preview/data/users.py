# Hardcoded user registry.
# To generate hashes for new passwords, run: python add_user.py
# Then paste the output line into USERS below.

USERS = {
    # "username": "werkzeug-hash"
    # Paste generated hashes here, e.g.:
    "mebertK9": "scrypt:32768:8:1$9KRTrQQc4fE6gcwd$6e3908367901f8e091d123893d9ba6269cbde7d0b6d2e309bcd679d551dfe896254aa79949904785eecef5cbfee1fe3ab1a542305e64cbb85daab7569f0c35e1",
    "Maxi": "scrypt:32768:8:1$Q6y4y6JdLNiUiBHX$ade0f3b381b4393adc155c8020c265880c4bbc680345ca9534bd051579684991c5ed0ce77dd4a5430d097d86b742ef4dc725aee4aaeb1e39e70577b3613112d8",
    "Dennis": "scrypt:32768:8:1$oPYbUmcsPcMp898f$a3eacc0cc0ba351e8169bb59d8057e24bbfcd7f06649923ee8a66c446d3ab5eb2b36daaa727126bd90c323b6f64c59c63813201d0350a7b683a74944c4f0b862",
    "Sassi": "scrypt:32768:8:1$wXmfgpRowq4LPX9x$f3e6757da3bf011171192e79ee7a2165afc3a3a090dfe97307938ad89295c435e45b8d17d897c08cc90bae8840de96724cee8127fbbce3e29bab272abd813f2d",
}

# Only this user sees the lock icon (finalize game).
# No backend enforcement — by design.
ADMIN_USER = "mebertK9"