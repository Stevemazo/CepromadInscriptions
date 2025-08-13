from flask import Flask, render_template, make_response, redirect, url_for, request, jsonify,session, flash, send_file, make_response
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import current_app


import zipfile
import tempfile
import base64
import requests
# from weasyprint import HTML
import os
import uuid

from mysql.connector import Error
from config import DB_CONFIG

from flask_mail import Mail, Message
import random

import smtplib
from flask import session


from io import BytesIO


app = Flask(__name__)

app.secret_key = "a4s4powerful"  # Clé secrète pour gérer les sessions

# Ensuite dans les routes : 
# pdfkit.from_string(html_bulletin, False, configuration=pdfkit_config)

# Connexion à la base de données MySQL
def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

# === CONFIG CINETPAY ===
API_KEY = '107142544768920942e315e4.71422111'
SITE_ID = '105904574'
CINETPAY_URL = 'https://api-checkout.cinetpay.com/v2/payment'

# ✅ Configuration Flask-Mail (place ceci ici)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'universiteducepromad01@gmail.com'
app.config['MAIL_PASSWORD'] = 'jktj wpvy kgtq ppbj'
app.config['MAIL_DEFAULT_SENDER'] = 'universiteducepromad01@gmail.com'

mail = Mail(app)

def generer_matricule(mysql):
    try:
        # Connexion au curseur via Flask MySQL

        conn = connect_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT nom_etablissement FROM etablissement LIMIT 1")
        row = cur.fetchone()
        conn.close()

        nom_ecole = row['nom_etablissement'] if row and row['nom_etablissement'] else "ECOLE"

    except Exception as e:
        print("❌ Erreur récupération du nom d'établissement :", e)
        nom_ecole = "ECOLE"

    # Génère 4 chiffres aléatoires
    chiffres = ''.join(str(random.randint(0, 9)) for _ in range(4))

    # Assemble proprement le matricule
    return f"{nom_ecole.upper().replace(' ', '').replace('-', '')}{chiffres}"


def envoyer_email(destinataire, code):
    sujet = "Code de confirmation - Votre inscription"
    message = f"Bonjour,\n\nVoici votre code de confirmation : {code}\n\nMerci."
    texte = f"Subject: {sujet}\n\n{message}"

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as serveur:
            serveur.login("universiteducepromad01@gmail.com", "jktj wpvy kgtq ppbj")
            serveur.sendmail("universiteducepromad01@gmail.com", destinataire, texte)
    except Exception as e:
        print("Erreur lors de l'envoi de l'e-mail :", e)


@app.context_processor
def inject_nom_etablissement():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT nom_etablissement FROM etablissement LIMIT 1")
    row = cur.fetchone()
    conn.close()
    nom_etablissement = row['nom_etablissement'] if row else "Nom de l'École"
    
    return dict(nom_etablissement=nom_etablissement)

@app.context_processor
def inject_recrutement_actif():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT verification_actif FROM configuration WHERE id = 1")
    actif = cur.fetchone()['verification_actif']
    conn.close()
    return dict(verification_actif=actif)


# ----------------------- AUTHENTIFICATION ------------------------

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = connect_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_nom'] = user['nom']
            session['user_role'] = user['role']

            return redirect(url_for('dashboard'))
        flash("Email ou mot de passe incorrect", "danger")
    return render_template('login.html')

# ----------------------- CREATION COMPTE UTILISATEUR ------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    # Récupérer toutes les classes pour les afficher dans le formulaire


    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        
        cur.execute("INSERT INTO users (nom, email, password, role) VALUES (%s, %s, %s, %s)", 
                    (nom, email, password, role))
        conn.commit()
        conn.close()
        flash("Inscription réussie", "success")
        return redirect(url_for('login'))
    return render_template('register.html')


# ----------------------- PROFIL UTILISATEUR ------------------------
@app.route('/profil', methods=['GET', 'POST'])
def profil():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT nom, email FROM users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()

    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']
        password = request.form['password']

        if password:
            hashed = generate_password_hash(password)
            cur.execute("UPDATE users SET nom=%s, email=%s, password=%s WHERE id=%s", (nom, email, hashed, session['user_id']))
        else:
            cur.execute("UPDATE users SET nom=%s, email=%s WHERE id=%s", (nom, email, session['user_id']))

        conn.commit()
        flash("Profil mis à jour avec succès", "success")
        return redirect(url_for('login'))

    return render_template('profil.html', user=user)


# ----------------------- SUPPRIMER UN COMPTE UTILISATEUR ------------------------

@app.route('/supprimer_compte', methods=['POST'])
def supprimer_compte():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("DELETE FROM users WHERE id = %s", (session['user_id'],))
    conn.commit()

    session.clear()
    flash("Compte supprimé avec succès", "success")
    return redirect(url_for('login'))

# ----------------------- DECONNEXION ------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ----------------------- Dashboard ------------------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    # Infos de l'établissement
    cur.execute("SELECT nom_etablissement, lieu, adresse, commune, province, code, annee_scolaire FROM etablissement LIMIT 1")
    etab = cur.fetchone()

    etablissement = {
        'nom': etab['nom_etablissement'],
        'lieu': etab['lieu'],
        'adresse': etab['adresse'],
        'commune': etab['commune'],
        'province': etab['province'],
        'code': etab['code'],
        'annee_scolaire': etab['annee_scolaire']
    }

    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        actif = 1 if 'verification_actif' in request.form else 0
        cur.execute("UPDATE configuration SET verification_actif = %s WHERE id = 1", (actif,))
        conn.commit()
        flash("État de recrutement mis à jour avec succès.", "success")

    return render_template('dashboard.html', etablissement=etablissement)


# ----------------------- CRUD: ETABLISSEMENT ------------------------

@app.route('/etablissement')
def gestion_etablissement():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM etablissement")
    etablissements = cur.fetchall()
    conn.commit()

    conn.close()
    return render_template("gestion_etablissement.html", etablissements=etablissements)


@app.route('/add_etablissement', methods=['POST'])
def add_etablissement():
    nom_etablissement = request.form['nom_etablissement']
    lieu = request.form['lieu']
    adresse = request.form['adresse']
    commune = request.form['commune']
    province = request.form['province']
    code = request.form['code']
    annee_scolaire = request.form['annee_scolaire']
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("INSERT INTO etablissement (nom_etablissement, lieu, adresse, commune, province, code, annee_scolaire) VALUES (%s, %s, %s, %s, %s, %s, %s)", (nom_etablissement, lieu, adresse, commune, province, code, annee_scolaire,))
    conn.commit()
    conn.close()
    return redirect(url_for('gestion_etablissement'))


@app.route('/delete_etablissement/<int:id>')
def delete_etablissement(id):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("DELETE FROM etablissement WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('gestion_etablissement'))


@app.route('/edit_etablissement/<int:id>', methods=['GET', 'POST'])
def edit_etablissement(id):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    if request.method == 'POST':
        nom_etablissement = request.form['nom_etablissement']
        lieu = request.form['lieu']
        adresse = request.form['adresse']
        commune = request.form['commune']
        province = request.form['province']
        code = request.form['code']
        annee_scolaire = request.form['annee_scolaire']
        cur.execute("UPDATE etablissement SET nom_etablissement = %s, lieu = %s, adresse = %s, commune = %s, province = %s, code = %s, annee_scolaire = %s WHERE id = %s", (nom_etablissement, lieu, adresse, commune, province, code, annee_scolaire, id))
        conn.commit()
        conn.close()
        return redirect(url_for('gestion_etablissement'))

    cur.execute("SELECT * FROM etablissement WHERE id = %s", (id,))
    etablissement = cur.fetchone()
    conn.commit()


    col_names = [desc[0] for desc in cur.description]

    conn.close()
    return render_template("edit_etablissement.html", etablissement=etablissement)


@app.route('/verifier_email', methods=['GET', 'POST'])
def etudiant_inscription_email():
    if request.method == 'POST':
        email = request.form['email']
        # conn = connect_db()
        # cur = conn.cursor(dictionary=True)
        # cur.execute("SELECT id FROM inscriptions_etudiants WHERE email = %s", (email,))
        # existing = cur.fetchone()

        # if existing:
        #     flash("Cet e-mail est déjà utilisé pour une inscription.", "danger")
        #     return redirect(url_for('etudiant_inscription_email'))

        # Générer un code
        code = str(random.randint(100000, 999999))
        session['pending_email'] = email
        session['verification_code'] = code
        envoyer_email(email, code)

        flash("Un code de confirmation a été envoyé à votre adresse e-mail.", "info")
        # conn = connect_db()
        # cur = conn.cursor(dictionary=True)
        # cur.execute("INSERT INTO inscriptions_etudiants (email) VALUES (%s)", (email,))
        # conn.commit()
        # conn.close()
        return redirect(url_for('confirmation_connexion'))

    return render_template('inscription_email.html')


@app.route('/confirmation', methods=['GET', 'POST'])
def confirmation_connexion():
    if request.method == 'POST':
        code_saisi = request.form['code']
        code_envoye = session.get('verification_code')
        email = session.get('pending_email')

        if code_saisi == code_envoye:
            flash("Code vérifié. Poursuivez votre inscription.", "success")

            session['email_connecte'] = email
            
            return redirect(url_for('inscription_etudiant'))
        else:
            flash("Code incorrect. Réessayez.", "danger")
            return redirect(url_for('confirmation_connexion'))

    return render_template('confirmation_connexion.html')


@app.route('/inscription_finale', methods=['GET', 'POST'])
def inscription_etudiant():

    if request.method == 'POST':
        # Données personnelles
        nom = request.form['nom']
        postnom = request.form['postnom']
        prenom = request.form['prenom']
        email = request.form['email']
        date_naissance = request.form['date_naissance']
        sexe = request.form['sexe']
        etat_civil = request.form['etat_civil']
        nom_conjoint = request.form.get('nom_conjoint') or None
        adresse = request.form['adresse']
        telephone = request.form['telephone']
        nom_tuteur = request.form.get('nom_tuteur') or None
        adresse_tuteur = request.form.get('adresse_tuteur') or None
        telephone_tuteur = request.form.get('telephone_tuteur') or None
        allergies = request.form.get('allergies')
        systeme_id = request.form['systeme_id']
        promotion_id = request.form['promotion_id']
        inscription_id = request.form['inscription_id']
        montant_inscription = request.form['montant_inscription']
        devise = request.form['devise']
        transaction_id = str(uuid.uuid4())
        statut_paiement = 'EN_ATTENTE'

        conn = connect_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("""SELECT id FROM etudiants WHERE nom=%s AND postnom=%s AND prenom=%s AND email=%s 
        AND systeme_id=%s AND promotion_id=%s AND inscription_id=%s AND statut_paiement='PAYÉ'
        """, (nom, postnom, prenom, email, systeme_id, promotion_id, inscription_id, statut_paiement))

        doublon = cur.fetchone()

        if doublon:
            conn.close()

            flash("Cette inscription existe déjà dans le système.", "danger")
            return redirect(url_for('inscription_etudiant'))

        # Traitement de l’image
        photo_data = request.form.get('photo_data')
        photo_file = request.files.get('photo')
        photo_filename = None
        if photo_data:
            photo_filename = f"{uuid.uuid4()}.png"
            with open(f'static/uploads/{photo_filename}', 'wb') as f:
                f.write(base64.b64decode(photo_data.split(',')[1]))
        elif photo_file and photo_file.filename:
            photo_filename = secure_filename(photo_file.filename)
            photo_file.save(f'static/uploads/{photo_filename}')

        # Gestion des pièces jointes
        def save_file(field_name):
            f = request.files.get(field_name)
            if f and f.filename:
                filename = f"{uuid.uuid4()}_{secure_filename(f.filename)}"
                path = os.path.join('static/uploads', filename)
                f.save(path)
                return filename
            return None

        bulletin1 = save_file('bulletin1')
        bulletin2 = save_file('bulletin2')
        attestation_reussite = save_file('attestation_reussite')
        attestation_moeurs = save_file('attestation_moeurs')
        certificat_naissance = save_file('certificat_naissance')


        # Insertion en attente dans la base de données
        conn = connect_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            INSERT INTO etudiants (
                nom, postnom, prenom, email, date_naissance, sexe, etat_civil, nom_conjoint,
                adresse, telephone, photo, nom_tuteur, adresse_tuteur, telephone_tuteur,
                allergies, systeme_id, promotion_id,
                bulletin1, bulletin2, attestation_reussite, attestation_moeurs,
                inscription_id, montant_inscription, devise, transaction_id, statut_paiement
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            nom, postnom, prenom, email, date_naissance, sexe, etat_civil, nom_conjoint,
            adresse, telephone, photo_filename, nom_tuteur, adresse_tuteur, telephone_tuteur,
            allergies, systeme_id, promotion_id,
            bulletin1, bulletin2, attestation_reussite, attestation_moeurs,
            inscription_id, montant_inscription, devise, transaction_id, statut_paiement
        ))
        conn.commit()
        conn.close()

        # Redirection vers CinetPay
        data = {
            "amount": montant_inscription,
            "currency": devise,
            "apikey": API_KEY,
            "site_id": SITE_ID,
            "transaction_id": transaction_id,
            "description": f"Inscription {prenom} {nom}",
            "customer_name": nom,
            "customer_surname": prenom,
            "customer_email": email,
            "customer_phone_number": telephone,
            "notify_url": request.url_root + 'notification',
            "return_url": request.url_root + 'success?transaction_id=' + transaction_id
        }

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(CINETPAY_URL, json=data, headers=headers)
        result = response.json()

        if result.get("code") == '201':
            return redirect(result['data']['payment_url'])
        else:
            return f"Erreur lors de l'initialisation du paiement: {result}"

    email_connecte = session.get('email_connecte')

    # GET
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM systemes")
    systemes = cur.fetchall()
    cur.execute("SELECT * FROM promotions")
    promotions = cur.fetchall()
    cur.execute("SELECT * FROM type_inscriptions")
    inscriptions = cur.fetchall()
    return render_template('inscription.html', systemes=systemes, promotions=promotions, inscriptions=inscriptions, email_connecte=email_connecte)


# === WEBHOOK / CALLBACK ===
@app.route('/notification', methods=['POST'])
def notification():
    data = request.json
    transaction_id = data.get('transaction_id')

    if transaction_id:
        # Vérifie le paiement via CinetPay
        verify_url = 'https://api-checkout.cinetpay.com/v2/payment/check'
        payload = {
            "apikey": API_KEY,
            "site_id": SITE_ID,
            "transaction_id": transaction_id
        }

        headers = {
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(verify_url, json=payload, headers=headers)
            result = response.json()

            # Vérifie si le paiement est bien accepté
            statut_paiement = result.get("data", {}).get("status")
            if statut_paiement == 'ACCEPTED':
                conn = connect_db()
                cur = conn.cursor(dictionary=True)
                cur.execute("UPDATE etudiants SET statut_paiement='PAYÉ' WHERE transaction_id=%s", (transaction_id,))
                conn.commit()
                conn.close()
        except Exception as e:
            print("Erreur lors de la vérification du paiement :", e)

    return "OK", 200


# === PAGE DE RETOUR ===
@app.route('/success', methods=['GET', 'POST'])
def success():
    transaction_id = request.args.get('transaction_id')

    if not transaction_id:
        return "Transaction ID manquant dans l'URL."

    # Vérification du statut réel auprès de CinetPay
    url = "https://api-checkout.cinetpay.com/v2/payment/check"
    payload = {
        "apikey": API_KEY,
        "site_id": SITE_ID,
        "transaction_id": transaction_id
    }
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=payload, headers=headers)
    result = response.json()

    if result.get('code') == '00' and result['data'].get('status') == 'ACCEPTED':
        # Paiement réussi : mettre à jour le statut
        conn = connect_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("UPDATE etudiants SET statut_paiement=%s WHERE transaction_id=%s", ('PAYÉ', transaction_id))
        conn.commit()

        # 🔍 Récupérer les infos du paiement
        cur.execute("SELECT nom, prenom, montant_inscription, devise FROM etudiants WHERE transaction_id=%s", (transaction_id,))
        paiement = cur.fetchone()
        conn.close()

        if paiement:
            nom, prenom, montant_inscription, devise = paiement
            return render_template('success.html',
                                   nom=nom,
                                   prenom=prenom,
                                   montant_inscription=montant_inscription,
                                   devise=devise)
        else:
            return "Paiement mis à jour mais les données n'ont pas pu être récupérées."
    else:
        # Paiement échoué ou en attente
        return f"Le paiement n’a pas été validé : {result.get('message', 'Erreur inconnue')}"


@app.route('/manage_etudiants')
def manage_etudiants():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    # Récupérer les étudiants NON validés
    cur.execute("""
        SELECT * FROM etudiants
        WHERE inscription_validee = FALSE AND statut_paiement ='PAYÉ' OR inscription_validee IS NULL
        ORDER BY id DESC
    """)
    etudiants_non_valides = cur.fetchall()

    # Récupérer les étudiants VALIDÉS
    cur.execute("""
        SELECT * FROM etudiants
        WHERE inscription_validee = TRUE AND statut_paiement ='PAYÉ'
        ORDER BY date_inscription DESC
    """)
    etudiants_valides = cur.fetchall()

    cur.execute("SELECT * FROM systemes")
    systemes = cur.fetchall()
    cur.execute("SELECT * FROM promotions")
    promotions = cur.fetchall()

    return render_template(
        'manage_etudiants.html',
        etudiants_non_valides=etudiants_non_valides,
        etudiants_valides=etudiants_valides, systemes=systemes, promotions=promotions
    )



@app.route('/modifier_etudiant/<int:id>', methods=['POST'])
def modifier_etudiant(id):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    # Données du formulaire
    nom = request.form['nom']
    prenom = request.form['prenom']
    email = request.form['email']
    date_naissance = request.form['date_naissance']
    sexe = request.form['sexe']
    etat_civil = request.form['etat_civil']
    nom_conjoint = request.form.get('nom_conjoint')
    adresse = request.form['adresse']
    telephone = request.form['telephone']

    photo_data = request.form.get('photo_data')
    photo_file = request.files.get('photo')
    photo_filename = None

    if photo_data:
        import base64, uuid
        photo_filename = f"{uuid.uuid4()}.png"
        with open(f'static/uploads/{photo_filename}', 'wb') as f:
            f.write(base64.b64decode(photo_data.split(',')[1]))
    elif photo_file and photo_file.filename:
        photo_filename = photo_file.filename
        photo_file.save(f'static/uploads/{photo_filename}')
    else:
        # Garder l’ancienne photo si aucune nouvelle n’est fournie
        cur.execute("SELECT photo FROM etudiants WHERE id = %s", (id,))
        photo_filename = cur.fetchone()['photo']

    nom_tuteur = request.form.get('nom_tuteur')
    adresse_tuteur = request.form.get('adresse_tuteur')
    telephone_tuteur = request.form.get('telephone_tuteur')
    allergies = request.form.get('allergies')
    systeme_id = request.form['systeme_id']
    promotion_id = request.form['promotion_id']
    numero_matricule = request.form['numero_matricule']

    # Mise à jour en base de données
    cur.execute("""
        UPDATE etudiants
        SET nom=%s, prenom=%s, email=%s, date_naissance=%s, sexe=%s, etat_civil=%s,
            nom_conjoint=%s, adresse=%s, telephone=%s, photo=%s,
            nom_tuteur=%s, adresse_tuteur=%s, telephone_tuteur=%s, allergies=%s,
            systeme_id=%s, promotion_id=%s, numero_matricule=%s
        WHERE id=%s
    """, (
        nom, prenom, email, date_naissance, sexe, etat_civil, nom_conjoint,
        adresse, telephone, photo_filename, nom_tuteur, adresse_tuteur,
        telephone_tuteur, allergies, systeme_id, promotion_id, numero_matricule,
        id
    ))

    conn.commit()
    flash("Étudiant mis à jour avec succès", "success")
    return redirect(url_for('manage_etudiants'))
    

@app.route('/supprimer_etudiant/<int:id>', methods=['POST'])
def supprimer_etudiant(id):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    
    # On récupère le nom du fichier photo pour le supprimer aussi du disque si nécessaire
    cur.execute("SELECT photo FROM etudiants WHERE id = %s", (id,))
    photo = cur.fetchone()
    if photo and photo['photo']:
        import os
        photo_path = os.path.join('static/uploads', photo['photo'])
        if os.path.exists(photo_path):
            os.remove(photo_path)
    
    # Suppression dans la base de données
    cur.execute("DELETE FROM etudiants WHERE id = %s", (id,))
    conn.commit()
    flash("Étudiant supprimé avec succès", "success")
    return redirect(url_for('manage_etudiants'))


@app.route('/voir_documents/<int:etudiant_id>')
def voir_documents(etudiant_id):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT nom, prenom, bulletin1, bulletin2, attestation_reussite, attestation_moeurs, certificat_naissance
        FROM etudiants WHERE id = %s
    """, (etudiant_id,))
    etudiant = cur.fetchone()
    conn.close()

    if not etudiant:
        return "Étudiant introuvable", 404

    return render_template('voir_documents.html', etudiant=etudiant)


@app.route('/valider_etudiant/<int:id>', methods=['POST'])
def valider_etudiant(id):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    # 1. Vérifier si l'étudiant existe
    cur.execute("SELECT email, nom, prenom FROM etudiants WHERE id = %s", (id,))
    etudiant = cur.fetchone()

    if not etudiant:
        flash("Étudiant introuvable", "danger")
        return redirect(url_for('manage_etudiants'))

    email = etudiant['email']
    nom = etudiant['nom']
    prenom = etudiant['prenom']

    # 2. Générer le numéro matricule
    numero_matricule = generer_matricule(mysql)

    # 3. Mettre à jour la base
    cur.execute("""
        UPDATE etudiants
        SET inscription_validee = TRUE, numero_matricule = %s, date_inscription = NOW()
        WHERE id = %s
    """, (numero_matricule, id))
    conn.commit()

    # 4. Envoyer l’email à l’étudiant
    try:
        msg = Message("Confirmation provisoire de votre inscription",
                      recipients=[email])
        msg.body = f"""
Bonjour {prenom} {nom},

Votre inscription a été validée provisoirement.

Voici votre numéro matricule : {numero_matricule}

Veuillez vous présenter à l’apparitorat pour déposer les documents requis afin de finaliser votre inscription.

Cordialement,
Le Secrétariat Académique
"""
        mail.send(msg)
    except Exception as e:
        flash("Inscription validée mais erreur lors de l’envoi de l’email : " + str(e), "warning")
    else:
        flash("Inscription validée et email envoyé avec succès", "success")

    return redirect(url_for('manage_etudiants'))


@app.route('/manage_systemes')
def manage_systemes():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM systemes")
    systemes = cur.fetchall()
    return render_template('manage_systemes.html', systemes=systemes)


@app.route('/add_systeme', methods=['POST'])
def add_systeme():
    nom = request.form['nom']
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("INSERT INTO systemes (nom) VALUES (%s)", (nom,))
    conn.commit()
    return redirect(url_for('manage_systemes'))


@app.route('/update_systeme/<int:id>', methods=['POST'])
def update_systeme(id):
    nom = request.form['nom']
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("UPDATE systemes SET nom=%s WHERE id=%s", (nom, id))
    conn.commit()
    return redirect(url_for('manage_systemes'))


@app.route('/delete_systeme/<int:id>')
def delete_systeme(id):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("DELETE FROM systemes WHERE id=%s", (id,))
    conn.commit()
    return redirect(url_for('manage_systemes'))


@app.route('/manage_facultes')
def manage_facultes():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM facultes")
    facultes = cur.fetchall()
    return render_template('manage_facultes.html', facultes=facultes)


@app.route('/add_faculte', methods=['POST'])
def add_faculte():
    nom = request.form['nom']
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("INSERT INTO facultes (nom) VALUES (%s)", (nom,))
    conn.commit()
    return redirect(url_for('manage_facultes'))


@app.route('/update_faculte/<int:id>', methods=['POST'])
def update_faculte(id):
    nom = request.form['nom']
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("UPDATE facultes SET nom=%s WHERE id=%s", (nom, id))
    conn.commit()
    return redirect(url_for('manage_facultes'))


@app.route('/delete_faculte/<int:id>')
def delete_faculte(id):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("DELETE FROM facultes WHERE id=%s", (id,))
    conn.commit()
    return redirect(url_for('manage_facultes'))


@app.route('/manage_departements')
def manage_departements():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT d.id, d.nom, d.faculte_id, f.nom AS faculte_nom FROM departements d JOIN facultes f ON d.faculte_id = f.id")
    departements = cur.fetchall()

    cur.execute("SELECT * FROM facultes")
    facultes = cur.fetchall()
    return render_template('manage_departements.html', departements=departements, facultes=facultes)


@app.route('/add_departement', methods=['POST'])
def add_departement():
    nom = request.form['nom']
    faculte_id = request.form['faculte_id']
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("INSERT INTO departements (nom, faculte_id) VALUES (%s, %s)", (nom, faculte_id))
    conn.commit()
    return redirect(url_for('manage_departements'))


@app.route('/update_departement/<int:id>', methods=['POST'])
def update_departement(id):
    nom = request.form['nom']
    faculte_id = request.form['faculte_id']
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("UPDATE departements SET nom=%s, faculte_id=%s WHERE id=%s", (nom, faculte_id, id))
    conn.commit()
    return redirect(url_for('manage_departements'))


@app.route('/delete_departement/<int:id>')
def delete_departement(id):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("DELETE FROM departements WHERE id=%s", (id,))
    conn.commit()
    return redirect(url_for('manage_departements'))


@app.route('/manage_options')
def manage_options():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT o.id, o.nom, o.departement_id, d.nom AS departement_nom 
        FROM options o 
        JOIN departements d ON o.departement_id = d.id
    """)
    options = cur.fetchall()

    cur.execute("SELECT * FROM departements")
    departements = cur.fetchall()
    return render_template('manage_options.html', options=options, departements=departements)


@app.route('/add_option', methods=['POST'])
def add_option():
    nom = request.form['nom']
    departement_id = request.form['departement_id']
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("INSERT INTO options (nom, departement_id) VALUES (%s, %s)", (nom, departement_id))
    conn.commit()
    return redirect(url_for('manage_options'))


@app.route('/update_option/<int:id>', methods=['POST'])
def update_option(id):
    nom = request.form['nom']
    departement_id = request.form['departement_id']
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("UPDATE options SET nom=%s, departement_id=%s WHERE id=%s", (nom, departement_id, id))
    conn.commit()
    return redirect(url_for('manage_options'))


@app.route('/delete_option/<int:id>')
def delete_option(id):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("DELETE FROM options WHERE id=%s", (id,))
    conn.commit()
    return redirect(url_for('manage_options'))


@app.route('/manage_promotions')
def manage_promotions():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT p.id, p.nom, p.option_id, p.systeme_id, o.nom AS option_nom, s.nom AS systeme_nom 
        FROM promotions p 
        JOIN options o ON p.option_id = o.id
        JOIN systemes s ON p.systeme_id = s.id
    """)
    promotions = cur.fetchall()

    cur.execute("SELECT * FROM options")
    options = cur.fetchall()
    cur.execute("SELECT * FROM systemes")
    systemes = cur.fetchall()
    return render_template('manage_promotions.html', promotions=promotions, options=options, systemes=systemes)


@app.route('/add_promotion', methods=['POST'])
def add_promotion():
    nom = request.form['nom']
    option_id = request.form['option_id']
    systeme_id = request.form['systeme_id']
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("INSERT INTO promotions (nom, option_id, systeme_id) VALUES (%s, %s, %s)", (nom, option_id, systeme_id))
    conn.commit()
    return redirect(url_for('manage_promotions'))


@app.route('/update_promotion/<int:id>', methods=['POST'])
def update_promotion(id):
    nom = request.form['nom']
    option_id = request.form['option_id']
    systeme_id = request.form['systeme_id']
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("UPDATE promotions SET nom=%s, option_id=%s, systeme_id=%s WHERE id=%s", (nom, option_id, systeme_id, id))
    conn.commit()
    return redirect(url_for('manage_promotions'))


@app.route('/delete_promotion/<int:id>')
def delete_promotion(id):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("DELETE FROM promotions WHERE id=%s", (id,))
    conn.commit()
    return redirect(url_for('manage_promotions'))

@app.route('/manage_inscriptions')
def manage_inscriptions():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM type_inscriptions")
    inscriptions = cur.fetchall()
    conn.commit()
    return render_template('manage_inscriptions.html', inscriptions=inscriptions)

@app.route('/ajouter_inscription', methods=['POST'])
def ajouter_inscription():
    nom = request.form['nom']
    montant = request.form['montant']
    devise = request.form['devise']
    
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute('INSERT INTO type_inscriptions (nom, montant, devise) VALUES (%s, %s, %s)',
                 (nom, montant, devise))
    conn.commit()
    
    flash('Type d\'inscription ajouté avec succès !')
    return redirect(url_for('manage_inscriptions'))

@app.route('/modifier_inscription/<int:id>', methods=['POST'])
def modifier_inscription(id):
    nom = request.form['nom']
    montant = request.form['montant']
    devise = request.form['devise']
    
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute('UPDATE type_inscriptions SET nom = %s, montant = %s, devise = %s WHERE id = %s',
                 (nom, montant, devise, id))
    conn.commit()
    
    flash('Type d\'inscription modifié avec succès !')
    return redirect(url_for('manage_inscriptions'))

@app.route('/supprimer_inscription/<int:id>')
def supprimer_inscription(id):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute('DELETE FROM type_inscriptions WHERE id = %s', (id,))
    conn.commit()
    
    flash('Type d\'inscription supprimé avec succès !')
    return redirect(url_for('manage_inscriptions'))

# ----------------------- RUN ------------------------

if __name__ == '__main__':
    app.run(debug=True)
