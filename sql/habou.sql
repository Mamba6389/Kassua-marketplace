-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1
-- Généré le : mar. 06 jan. 2026 à 13:47
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
-- Base de données : `habou`
--

-- --------------------------------------------------------

--
-- Structure de la table `carts`
--

CREATE TABLE `carts` (
  `id` int(11) NOT NULL,
  `username` varchar(150) NOT NULL,
  `produit` varchar(150) NOT NULL,
  `prix` varchar(50) DEFAULT NULL,
  `vendeur` varchar(150) DEFAULT NULL,
  `contact` varchar(150) DEFAULT NULL,
  `categorie` varchar(150) DEFAULT NULL,
  `ville` varchar(100) DEFAULT NULL,
  `date` varchar(50) DEFAULT NULL,
  `quantity` int(11) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `products`
--

CREATE TABLE `products` (
  `id` int(11) NOT NULL,
  `produit` varchar(150) NOT NULL,
  `ville` varchar(100) DEFAULT NULL,
  `prix` varchar(50) DEFAULT NULL,
  `date` varchar(50) DEFAULT NULL,
  `categorie` varchar(100) DEFAULT NULL,
  `vendeur` varchar(150) DEFAULT NULL,
  `contact` varchar(150) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `products`
--

INSERT INTO `products` (`id`, `produit`, `ville`, `prix`, `date`, `categorie`, `vendeur`, `contact`) VALUES
(4338, 'Pomme', 'Niamey', '0', '2024-01-15', 'fruits_legumes', '', ''),
(4339, 'Banane', 'Niamey', '0', '2024-01-16', 'fruits_legumes', NULL, NULL),
(4340, 'Orange', 'Niamey', '0', '2024-01-17', 'fruits_legumes', NULL, NULL),
(4341, 'Tomate', 'Niamey', '0', '2024-01-15', 'fruits_legumes', NULL, NULL),
(4342, 'Oignon', 'Niamey', '0', '2024-01-16', 'fruits_legumes', NULL, NULL),
(4343, 'Carotte', 'Niamey', '0', '2024-01-17', 'fruits_legumes', NULL, NULL),
(4344, 'Salade', 'Niamey', '0', '2024-01-17', 'fruits_legumes', NULL, NULL),
(4345, 'raisin', 'Niamey', '0', '2024-01-17', 'fruits_legumes', NULL, NULL),
(4346, 'Ananas', 'Niamey', '0', '2024-01-17', 'fruits_legumes', NULL, NULL),
(4347, 'poire', 'Niamey', '0', '2024-01-17', 'fruits_legumes', NULL, NULL),
(4348, 'choux', 'Niamey', '0', '2024-01-17', 'fruits_legumes', NULL, NULL),
(4349, 'Pastèque', 'Niamey', '0', '2024-01-17', 'fruits_legumes', NULL, NULL),
(4350, 'Aubergine', 'Niamey', '0', '2024-01-17', 'fruits_legumes', NULL, NULL),
(4351, 'Concombre', 'Niamey', '0', '2024-01-17', 'fruits_legumes', NULL, NULL),
(4352, 'poivron', 'Niamey', '0', '2024-01-17', 'fruits_legumes', NULL, NULL),
(4353, 'Piment', 'Niamey', '0', '2024-01-17', 'fruits_legumes', NULL, NULL),
(4354, 'Pomme de terre', 'Niamey', '0', '2024-01-17', 'fruits_legumes', NULL, NULL),
(4355, 'haricot vert', 'Niamey', '0', '2024-01-17', 'fruits_legumes', NULL, NULL),
(4356, 'tchappata et guisma', 'Niamey', '0', '2024-01-17', 'fruits_legumes', NULL, NULL),
(4357, 'Poulet', 'Niamey', '0', '2024-01-15', 'viandes_poissons', NULL, NULL),
(4358, 'Boeuf', 'Niamey', '0', '2024-01-16', 'viandes_poissons', NULL, NULL),
(4359, 'Poisson', 'Niamey', '0', '2024-01-17', 'viandes_poissons', NULL, NULL),
(4360, 'viande hachée', 'Niamey', '0', '2024-01-15', 'viandes_poissons', '', ''),
(4361, 'Lait', 'Niamey', '0', '2024-01-17', 'produits_laitiers', NULL, NULL),
(4362, 'Fromage', 'Niamey', '0', '2024-01-15', 'produits_laitiers', NULL, NULL),
(4363, 'Yaourt', 'Niamey', '0', '2024-01-16', 'produits_laitiers', NULL, NULL),
(4364, 'Beurre', 'Niamey', '0', '2024-01-17', 'produits_laitiers', NULL, NULL),
(4365, 'Crème', 'Niamey', '0', '2024-01-15', 'produits_laitiers', NULL, NULL),
(4366, 'sel', 'Niamey', '0', '2024-01-16', 'epicerie', '', ''),
(4367, 'Soumbala', 'Niamey', '0', '2024-01-17', 'epicerie', '', ''),
(4368, 'piment sec', 'Niamey', '0', '2024-01-15', 'epicerie', '', ''),
(4369, 'ail', 'Niamey', '0', '2024-01-16', 'epicerie', '', ''),
(4370, 'Canelle', 'Niamey', '0', '2024-01-17', 'epicerie', '', ''),
(4371, 'Percil et céleri', 'Niamey', '0', '2024-01-15', 'epicerie', '', ''),
(4372, 'Pain', 'Niamey', '0', '2024-01-16', 'boulangerie', NULL, NULL),
(4373, 'Croissant', 'Niamey', '0', '2024-01-17', 'boulangerie', NULL, NULL),
(4374, 'Cake', 'Niamey', '0', '2024-01-15', 'boulangerie', '', ''),
(4375, 'Eau', 'Niamey', '0', '2024-01-17', 'boissons', NULL, NULL),
(4376, 'Jus', 'Niamey', '0', '2024-01-15', 'boissons', NULL, NULL),
(4377, 'jus naturel', 'Niamey', '0', '2024-01-17', 'boissons', '', ''),
(4378, 'Boisson énergissante', 'Niamey', '0', '2024-01-15', 'boissons', '', ''),
(4379, 'poivre', 'Niamey', '0', '2024-01-18', 'epicerie', '', ''),
(4380, 'Yazi', 'Niamey', '0', '2025-12-23', 'epicerie', '', ''),
(4381, 'Clou de girofle', 'Niamey', '0', '2025-12-23', 'epicerie', '', ''),
(4382, 'Pilon', 'Niamey', '0', '2025-12-23', 'viandes_poissons', '', ''),
(4383, 'Pintade', 'Niamey', '0', '2025-12-23', 'viandes_poissons', '', ''),
(4384, 'Dinde', 'Niamey', '0', '2025-12-23', 'viandes_poissons', '', ''),
(4385, 'Gâteau', 'Niamey', '0', '2025-12-23', 'boulangerie', '', '');

-- --------------------------------------------------------

--
-- Structure de la table `purchases`
--

CREATE TABLE `purchases` (
  `id` int(11) NOT NULL,
  `produit` varchar(150) NOT NULL,
  `prix` varchar(50) DEFAULT NULL,
  `vendeur` varchar(150) DEFAULT NULL,
  `contact` varchar(150) DEFAULT NULL,
  `categorie` varchar(100) DEFAULT NULL,
  `date_achat` varchar(100) DEFAULT NULL,
  `acheteur` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Structure de la table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` varchar(100) DEFAULT NULL,
  `reset_token` varchar(255) DEFAULT NULL,
  `reset_expires` varchar(100) DEFAULT NULL,
  `is_admin` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Déchargement des données de la table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password`, `created_at`, `reset_token`, `reset_expires`, `is_admin`) VALUES
(12, 'azerty', 'azerty@gmail.com', 'f2d81a260dea8a100dd517984e53c56a7523d96942a834b9cdc249bd4e8c7aa9', '2025-12-21 15:06:06.914176', NULL, NULL, 0);

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `carts`
--
ALTER TABLE `carts`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `purchases`
--
ALTER TABLE `purchases`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `carts`
--
ALTER TABLE `carts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=40;

--
-- AUTO_INCREMENT pour la table `products`
--
ALTER TABLE `products`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4386;

--
-- AUTO_INCREMENT pour la table `purchases`
--
ALTER TABLE `purchases`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT pour la table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
