-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : lun. 11 août 2025 à 17:06
-- Version du serveur : 10.4.32-MariaDB
-- Version de PHP : 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `inscriptions_db`
--

-- --------------------------------------------------------

--
-- Structure de la table `configuration`
--

CREATE TABLE `configuration` (
  `id` int(11) NOT NULL,
  `verification_actif` tinyint(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `configuration`
--

INSERT INTO `configuration` (`id`, `verification_actif`) VALUES
(1, 1);

-- --------------------------------------------------------

--
-- Structure de la table `departements`
--

CREATE TABLE `departements` (
  `id` int(11) NOT NULL,
  `nom` varchar(255) DEFAULT NULL,
  `faculte_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Déchargement des données de la table `departements`
--

INSERT INTO `departements` (`id`, `nom`, `faculte_id`) VALUES
(4, 'Juridique', 1),
(5, 'Politico-Admin', 2);

-- --------------------------------------------------------

--
-- Structure de la table `etablissement`
--

CREATE TABLE `etablissement` (
  `id` int(11) NOT NULL,
  `nom_etablissement` text NOT NULL,
  `lieu` text NOT NULL,
  `adresse` text NOT NULL,
  `commune` text NOT NULL,
  `province` text NOT NULL,
  `code` text NOT NULL,
  `annee_scolaire` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `etablissement`
--

INSERT INTO `etablissement` (`id`, `nom_etablissement`, `lieu`, `adresse`, `commune`, `province`, `code`, `annee_scolaire`) VALUES
(1, 'UNIVERSITE DU CEPROMAD', 'kinshasa', 'avenue KIMPIOKA, N° 01, quartier 17 Mai ', 'Lemba', 'Kinshasa', 'AA304HY45879563', '2024-2025');

-- --------------------------------------------------------

--
-- Structure de la table `etudiants`
--

CREATE TABLE `etudiants` (
  `id` int(11) NOT NULL,
  `nom` varchar(100) DEFAULT NULL,
  `postnom` text NOT NULL,
  `prenom` varchar(100) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `date_naissance` date DEFAULT NULL,
  `sexe` enum('Masculin','Féminin') DEFAULT NULL,
  `etat_civil` enum('Célibataire','Marié(e)','Divorcé(e)','Veuf(ve)') DEFAULT NULL,
  `nom_conjoint` varchar(100) DEFAULT NULL,
  `adresse` text DEFAULT NULL,
  `telephone` varchar(20) DEFAULT NULL,
  `photo` varchar(255) DEFAULT NULL,
  `nom_tuteur` varchar(100) DEFAULT NULL,
  `adresse_tuteur` text DEFAULT NULL,
  `telephone_tuteur` varchar(20) DEFAULT NULL,
  `allergies` text DEFAULT NULL,
  `systeme_id` int(11) DEFAULT NULL,
  `promotion_id` int(11) DEFAULT NULL,
  `numero_matricule` varchar(50) DEFAULT NULL,
  `inscription_validee` tinyint(1) DEFAULT 0,
  `date_inscription` datetime DEFAULT current_timestamp(),
  `bulletin1` varchar(255) DEFAULT NULL,
  `bulletin2` varchar(255) DEFAULT NULL,
  `attestation_reussite` varchar(255) DEFAULT NULL,
  `attestation_moeurs` varchar(255) DEFAULT NULL,
  `inscription_id` int(11) DEFAULT NULL,
  `montant_inscription` int(11) DEFAULT NULL,
  `devise` varchar(10) DEFAULT NULL,
  `transaction_id` varchar(100) DEFAULT NULL,
  `statut_paiement` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Structure de la table `facultes`
--

CREATE TABLE `facultes` (
  `id` int(11) NOT NULL,
  `nom` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Déchargement des données de la table `facultes`
--

INSERT INTO `facultes` (`id`, `nom`) VALUES
(1, 'Droit administratif'),
(2, 'Sciences politiques');

-- --------------------------------------------------------

--
-- Structure de la table `inscriptions_etudiants`
--

CREATE TABLE `inscriptions_etudiants` (
  `id` int(11) NOT NULL,
  `email` varchar(150) NOT NULL,
  `date_creation` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Déchargement des données de la table `inscriptions_etudiants`
--

INSERT INTO `inscriptions_etudiants` (`id`, `email`, `date_creation`) VALUES
(1, 'mazosteve@gmail.com', '2025-08-10 20:08:03');

-- --------------------------------------------------------

--
-- Structure de la table `options`
--

CREATE TABLE `options` (
  `id` int(11) NOT NULL,
  `nom` varchar(255) DEFAULT NULL,
  `departement_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Déchargement des données de la table `options`
--

INSERT INTO `options` (`id`, `nom`, `departement_id`) VALUES
(2, 'Famille', 4),
(3, 'affaire', 4),
(4, 'urbanismes', 5);

-- --------------------------------------------------------

--
-- Structure de la table `promotions`
--

CREATE TABLE `promotions` (
  `id` int(11) NOT NULL,
  `nom` varchar(100) DEFAULT NULL,
  `option_id` int(11) DEFAULT NULL,
  `systeme_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Déchargement des données de la table `promotions`
--

INSERT INTO `promotions` (`id`, `nom`, `option_id`, `systeme_id`) VALUES
(2, 'Management', 3, 1),
(3, 'Génie Logiciel', 4, 2),
(5, 'steve mazo', 3, 2);

-- --------------------------------------------------------

--
-- Structure de la table `systemes`
--

CREATE TABLE `systemes` (
  `id` int(11) NOT NULL,
  `nom` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Déchargement des données de la table `systemes`
--

INSERT INTO `systemes` (`id`, `nom`) VALUES
(1, 'LMD'),
(2, 'Classique'),
(5, 'xxxx');

-- --------------------------------------------------------

--
-- Structure de la table `type_inscriptions`
--

CREATE TABLE `type_inscriptions` (
  `id` int(11) NOT NULL,
  `nom` text NOT NULL,
  `montant` double NOT NULL,
  `devise` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Déchargement des données de la table `type_inscriptions`
--

INSERT INTO `type_inscriptions` (`id`, `nom`, `montant`, `devise`) VALUES
(1, 'inscriptions', 100, 'CDF'),
(2, 'Reinscription', 35, 'USD');

-- --------------------------------------------------------

--
-- Structure de la table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `nom` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `role` enum('admin','prof') DEFAULT 'prof'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Déchargement des données de la table `users`
--

INSERT INTO `users` (`id`, `nom`, `email`, `password`, `role`) VALUES
(1, 'steve mazo', 'mazosteve@gmail.com', 'scrypt:32768:8:1$ef9pOYxZbs5QvG7j$cf15f5e2917c9183902789cd79f0b0594f38f379b293a053c67519eb3aa2a45fd54bcbe0f1338ca9100bf486fc51955860514d062ed4c9f525fd429cd5bfd469', 'admin'),
(6, 'Mbamvua Daniel', 'mazocorporation456@gmail.com', 'scrypt:32768:8:1$nJhovzGqskNP7qV8$46c118f3075cf912b6b1770fdc0410b60349af6b6a1bbddd87fc5f841d4988ebe36226f05d3361436ab31755db668b9386c5750f6531d16f1899daa6a52bab06', 'prof');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `configuration`
--
ALTER TABLE `configuration`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `departements`
--
ALTER TABLE `departements`
  ADD PRIMARY KEY (`id`),
  ADD KEY `faculte_id` (`faculte_id`);

--
-- Index pour la table `etablissement`
--
ALTER TABLE `etablissement`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `etudiants`
--
ALTER TABLE `etudiants`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_matricule` (`numero_matricule`),
  ADD KEY `systeme_id` (`systeme_id`),
  ADD KEY `promotion_id` (`promotion_id`),
  ADD KEY `inscription_id` (`inscription_id`);

--
-- Index pour la table `facultes`
--
ALTER TABLE `facultes`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `inscriptions_etudiants`
--
ALTER TABLE `inscriptions_etudiants`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Index pour la table `options`
--
ALTER TABLE `options`
  ADD PRIMARY KEY (`id`),
  ADD KEY `departement_id` (`departement_id`);

--
-- Index pour la table `promotions`
--
ALTER TABLE `promotions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `option_id` (`option_id`),
  ADD KEY `systeme_id` (`systeme_id`);

--
-- Index pour la table `systemes`
--
ALTER TABLE `systemes`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `type_inscriptions`
--
ALTER TABLE `type_inscriptions`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `configuration`
--
ALTER TABLE `configuration`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT pour la table `departements`
--
ALTER TABLE `departements`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT pour la table `etablissement`
--
ALTER TABLE `etablissement`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT pour la table `etudiants`
--
ALTER TABLE `etudiants`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `facultes`
--
ALTER TABLE `facultes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT pour la table `inscriptions_etudiants`
--
ALTER TABLE `inscriptions_etudiants`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT pour la table `options`
--
ALTER TABLE `options`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT pour la table `promotions`
--
ALTER TABLE `promotions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT pour la table `systemes`
--
ALTER TABLE `systemes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT pour la table `type_inscriptions`
--
ALTER TABLE `type_inscriptions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT pour la table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `departements`
--
ALTER TABLE `departements`
  ADD CONSTRAINT `departements_ibfk_1` FOREIGN KEY (`faculte_id`) REFERENCES `facultes` (`id`);

--
-- Contraintes pour la table `etudiants`
--
ALTER TABLE `etudiants`
  ADD CONSTRAINT `etudiants_ibfk_1` FOREIGN KEY (`systeme_id`) REFERENCES `systemes` (`id`),
  ADD CONSTRAINT `etudiants_ibfk_2` FOREIGN KEY (`promotion_id`) REFERENCES `promotions` (`id`),
  ADD CONSTRAINT `etudiants_ibfk_3` FOREIGN KEY (`inscription_id`) REFERENCES `type_inscriptions` (`id`);

--
-- Contraintes pour la table `options`
--
ALTER TABLE `options`
  ADD CONSTRAINT `options_ibfk_1` FOREIGN KEY (`departement_id`) REFERENCES `departements` (`id`);

--
-- Contraintes pour la table `promotions`
--
ALTER TABLE `promotions`
  ADD CONSTRAINT `promotions_ibfk_1` FOREIGN KEY (`option_id`) REFERENCES `options` (`id`),
  ADD CONSTRAINT `promotions_ibfk_2` FOREIGN KEY (`systeme_id`) REFERENCES `systemes` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
