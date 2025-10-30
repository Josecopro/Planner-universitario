import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { findPageByPath } from '../../constants/navigation';
import './NavBar.scss';

const DEFAULT_USER = {
	name: 'Usuario',
	role: 'Sin rol',
};

const formatSegment = (segment = '') =>
	segment
		.replace(/-/g, ' ')
		.replace(/\b\w/g, (char) => char.toUpperCase());

const createBreadcrumbs = (pathname) => {
	const segments = pathname.split('/').filter(Boolean);

	if (segments.length === 0) {
		return [];
	}

	let accumulatedPath = '';

	return segments.map((segment) => {
		accumulatedPath += `/${segment}`;
		const page = findPageByPath(accumulatedPath);

		return {
			path: accumulatedPath,
			label: page?.label ?? formatSegment(segment),
		};
	});
};

const getInitials = (name = '') =>
	name
		.split(' ')
		.filter(Boolean)
		.map((part) => part.charAt(0).toUpperCase())
		.slice(0, 2)
		.join('');

// Función para obtener datos del usuario desde localStorage
const getUserFromStorage = () => {
	try {
		const userStr = localStorage.getItem('user');
		if (!userStr) return null;
		
		const user = JSON.parse(userStr);
		console.log('📊 [NavBar] Usuario desde localStorage:', user);
		
		// Extraer nombre y rol del usuario
		const nombre = user.user_metadata?.nombre || user.nombre || user.email?.split('@')[0] || 'Usuario';
		const apellido = user.user_metadata?.apellido || user.apellido || '';
		const fullName = `${nombre} ${apellido}`.trim();
		
		// Extraer rol - puede venir de diferentes lugares
		const rol = user.user_metadata?.rol || 
		            user.rol?.nombre || 
		            user.rol_nombre || 
		            'Usuario';
		
		console.log('✅ [NavBar] Datos procesados:', { fullName, rol });
		
		return {
			name: fullName,
			role: rol
		};
	} catch (e) {
		console.error('❌ [NavBar] Error al parsear usuario:', e);
		return null;
	}
};

const NavBar = ({ user: userProp, onLogout }) => {
	const location = useLocation();
	const navigate = useNavigate();
	const [isMenuOpen, setIsMenuOpen] = useState(false);
	const [currentUser, setCurrentUser] = useState(DEFAULT_USER);
	const menuRef = useRef(null);

	// Actualizar usuario desde localStorage al montar y cuando cambie
	useEffect(() => {
		const updateUser = () => {
			const storedUser = getUserFromStorage();
			if (storedUser) {
				console.log('✅ [NavBar] Usuario actualizado:', storedUser);
				setCurrentUser(storedUser);
			} else if (userProp) {
				setCurrentUser(userProp);
			}
		};

		updateUser();

		// Escuchar cambios en localStorage (por si el usuario se actualiza en otra pestaña)
		window.addEventListener('storage', updateUser);
		
		return () => {
			window.removeEventListener('storage', updateUser);
		};
	}, [userProp]);

	const currentPage = useMemo(
		() => findPageByPath(location.pathname) ?? {
			label: 'Panel de control',
			icon: '📍',
		},
		[location.pathname]
	);

	const breadcrumbs = useMemo(
		() => createBreadcrumbs(location.pathname),
		[location.pathname]
	);

	useEffect(() => {
		const handleClickOutside = (event) => {
			if (!isMenuOpen) {
				return;
			}

			if (menuRef.current && !menuRef.current.contains(event.target)) {
				setIsMenuOpen(false);
			}
		};

		document.addEventListener('mousedown', handleClickOutside);
		return () => {
			document.removeEventListener('mousedown', handleClickOutside);
		};
	}, [isMenuOpen]);

	const toggleMenu = () => {
		setIsMenuOpen((prev) => !prev);
	};

	const closeMenu = () => setIsMenuOpen(false);

	const handleNavigate = (path) => {
		navigate(path);
		closeMenu();
	};

	const handleLogout = () => {
		closeMenu();

		// Limpiar localStorage
		localStorage.removeItem('user');
		localStorage.removeItem('supabase_session');
		console.log('✅ [NavBar] Sesión cerrada, localStorage limpiado');

		if (onLogout) {
			onLogout();
			return;
		}

		// Redirigir al login
		navigate('/login');
	};

	return (
		<header className="nav-bar">
			<div className="nav-bar__current">
				<div className="nav-bar__current-icon" aria-hidden="true">
					{currentPage.icon}
				</div>

				<div className="nav-bar__current-info">
					<span className="nav-bar__subtitle">Sección actual</span>
					<h1 className="nav-bar__title">{currentPage.label}</h1>
				</div>
			</div>

			<div className="nav-bar__details">
				{breadcrumbs.length > 0 && (
					<nav className="nav-bar__breadcrumbs" aria-label="Breadcrumb">
						<ul className="nav-bar__breadcrumb-list">
							<li className="nav-bar__breadcrumb-item">
								<Link className="nav-bar__breadcrumb-link" to="/">
									Inicio
								</Link>
							</li>
							{breadcrumbs.map(({ path, label }) => (
								<li key={path} className="nav-bar__breadcrumb-item">
									<span className="nav-bar__breadcrumb-separator">/</span>
									<Link className="nav-bar__breadcrumb-link" to={path}>
										{label}
									</Link>
								</li>
							))}
						</ul>
					</nav>
				)}

				<div className="nav-bar__profile" ref={menuRef}>
					<button
						type="button"
						className="nav-bar__profile-trigger"
						onClick={toggleMenu}
						aria-haspopup="true"
						aria-expanded={isMenuOpen}
					>
						<span className="nav-bar__avatar" aria-hidden="true">
							{getInitials(currentUser.name)}
						</span>

						<span className="nav-bar__profile-info">
							<span className="nav-bar__profile-name">{currentUser.name}</span>
							<span className="nav-bar__profile-role">{currentUser.role}</span>
						</span>

						<span className="nav-bar__profile-icon" aria-hidden="true">
							{isMenuOpen ? '▲' : '▼'}
						</span>
					</button>

					<div
						className={`nav-bar__menu ${isMenuOpen ? 'nav-bar__menu--open' : ''}`}
						role="menu"
					>
						<button
							type="button"
							className="nav-bar__menu-item"
							onClick={() => handleNavigate('/configuracion')}
							role="menuitem"
						>
							Configuración del perfil
						</button>
						<button
							type="button"
							className="nav-bar__menu-item nav-bar__menu-item--danger"
							onClick={handleLogout}
						>
							Cerrar sesión
						</button>
					</div>
				</div>
			</div>
		</header>
	);
};

export default NavBar;
