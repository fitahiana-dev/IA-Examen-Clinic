/**
 * App.jsx – version adaptée au TP "Éditeur de texte augmenté pour le Malagasy"
 */

import { useState, useEffect, useRef, useMemo } from 'react';
import { CKEditor } from '@ckeditor/ckeditor5-react';
import {
	DecoupledEditor,
	Autosave,
	Essentials,
	Paragraph,
	CloudServices,
	Autoformat,
	TextTransformation,
	LinkImage,
	Link,
	ImageBlock,
	ImageToolbar,
	BlockQuote,
	Bold,
	Bookmark,
	CKBox,
	ImageUpload,
	ImageInsert,
	ImageInsertViaUrl,
	AutoImage,
	PictureEditing,
	CKBoxImageEdit,
	CodeBlock,
	TableColumnResize,
	Table,
	TableToolbar,
	Emoji,
	Mention,
	PasteFromOffice,
	FindAndReplace,
	FontBackgroundColor,
	FontColor,
	FontFamily,
	FontSize,
	Fullscreen,
	Heading,
	HorizontalLine,
	ImageCaption,
	ImageResize,
	ImageStyle,
	Indent,
	IndentBlock,
	Code,
	Italic,
	AutoLink,
	ListProperties,
	List,
	MediaEmbed,
	RemoveFormat,
	SpecialCharactersArrows,
	SpecialCharacters,
	SpecialCharactersCurrency,
	SpecialCharactersEssentials,
	SpecialCharactersLatin,
	SpecialCharactersMathematical,
	SpecialCharactersText,
	Strikethrough,
	Subscript,
	Superscript,
	TableCaption,
	TableCellProperties,
	TableProperties,
	Alignment,
	TodoList,
	Underline,
	BalloonToolbar
} from 'ckeditor5';

import {
	AIChat,
	AIEditorIntegration,
	AIQuickActions,
	AIReviewMode,
	PasteFromOfficeEnhanced,
	FormatPainter,
	LineHeight,
	RealTimeCollaborativeComments,
	RealTimeCollaborativeEditing,
	PresenceList,
	Comments,
	RealTimeCollaborativeTrackChanges,
	TrackChanges,
	TrackChangesData,
	TrackChangesPreview,
	SlashCommand
} from 'ckeditor5-premium-features';

import 'ckeditor5/ckeditor5.css';
import 'ckeditor5-premium-features/ckeditor5-premium-features.css';

import './App.css';

const LICENSE_KEY =
	'eyJhbGciOiJFUzI1NiJ9.eyJleHAiOjE3NjczMTE5OTksImp0aSI6IjNlNjAwZDA3LTE4MmYtNGExYS05OTAwLTBhMTU1ZTQ5ODFhYyIsInVzYWdlRW5kcG9pbnQiOiJodHRwczovL3Byb3h5LWV2ZW50LmNrZWRpdG9yLmNvbSIsImRpc3RyaWJ1dGlvbkNoYW5uZWwiOlsiY2xvdWQiLCJkcnVwYWwiLCJzaCJdLCJ3aGl0ZUxhYmVsIjp0cnVlLCJsaWNlbnNlVHlwZSI6InRyaWFsIiwiZmVhdHVyZXMiOlsiKiJdLCJ2YyI6IjQ4M2YyZTg0In0.M-KkPQu8VzdyJSiB6ZEA4vKrmEaTubV8Ii-rNkFlkXVFVARFKCZDIeHzUV6xt7VkJaWrzOwXrU-CA3GKi9eWew';

// Pour la démo, on laisse un ID statique.
const DOCUMENT_ID = 'malagasy-editor-demo';

const CLOUD_SERVICES_TOKEN_URL =
	'https://y465r4yq8rq0.cke-cs.com/token/dev/f700269595c5d71da0e5c9cfda9f5c051e7233df14b34a1e7e1e64ead0c8?limit=10';
const CLOUD_SERVICES_WEBSOCKET_URL = 'wss://y465r4yq8rq0.cke-cs.com/ws';

/**
 * Règles phonotactiques simples côté front.
 * Ici on se contente de logger les problèmes ; tu pourras
 * ensuite les transformer en surlignage dans le texte.
 */
function checkMalagasyRules(text) {
	const errors = [];

	// Combinaisons interdites globalement ou en début de mot
	const forbiddenPatterns = [
		{ regex: /\b(nb|mk|nk)/gi, message: 'Combinaison impossible en début de mot en malagasy (nb, mk, nk).' },
		{ regex: /dt/gi, message: 'Séquence "dt" inhabituelle en malagasy.' },
		{ regex: /bp/gi, message: 'Séquence "bp" inhabituelle en malagasy.' },
		{ regex: /sz/gi, message: 'Séquence "sz" inhabituelle en malagasy.' }
	];

	for (const rule of forbiddenPatterns) {
		let match;
		while ((match = rule.regex.exec(text))) {
			errors.push({
				index: match.index,
				match: match[0],
				message: rule.message
			});
		}
	}

	return errors;
}

export default function App() {
	const editorPresenceRef = useRef(null);
	const editorContainerRef = useRef(null);
	const editorMenuBarRef = useRef(null);
	const editorToolbarRef = useRef(null);
	const editorRef = useRef(null);
	const editorAnnotationsRef = useRef(null);
	const editorCkeditorAiRef = useRef(null);
	const [isLayoutReady, setIsLayoutReady] = useState(false);
	const [malagasyErrors, setMalagasyErrors] = useState([]);

	useEffect(() => {
		setIsLayoutReady(true);
		return () => setIsLayoutReady(false);
	}, []);

	const { editorConfig } = useMemo(() => {
		if (!isLayoutReady) {
			return {};
		}

		return {
			editorConfig: {
				toolbar: {
					items: [
						'undo',
						'redo',
						'|',
						'trackChanges',
						'comment',
						'commentsArchive',
						'|',
						'toggleAi',
						'aiQuickActions',
						'|',
						'formatPainter',
						'findAndReplace',
						'fullscreen',
						'|',
						'heading',
						'|',
						'fontSize',
						'fontFamily',
						'fontColor',
						'fontBackgroundColor',
						'|',
						'bold',
						'italic',
						'underline',
						'strikethrough',
						'subscript',
						'superscript',
						'code',
						'removeFormat',
						'|',
						'emoji',
						'specialCharacters',
						'horizontalLine',
						'link',
						'bookmark',
						'insertImage',
						'insertImageViaUrl',
						'ckbox',
						'mediaEmbed',
						'insertTable',
						'blockQuote',
						'codeBlock',
						'|',
						'alignment',
						'lineHeight',
						'|',
						'bulletedList',
						'numberedList',
						'todoList',
						'outdent',
						'indent'
					],
					shouldNotGroupWhenFull: false
				},
				plugins: [
					AIChat,
					AIEditorIntegration,
					AIQuickActions,
					AIReviewMode,
					Alignment,
					Autoformat,
					AutoImage,
					AutoLink,
					Autosave,
					BalloonToolbar,
					BlockQuote,
					Bold,
					Bookmark,
					CKBox,
					CKBoxImageEdit,
					CloudServices,
					Code,
					CodeBlock,
					Comments,
					Emoji,
					Essentials,
					FindAndReplace,
					FontBackgroundColor,
					FontColor,
					FontFamily,
					FontSize,
					FormatPainter,
					Fullscreen,
					Heading,
					HorizontalLine,
					ImageBlock,
					ImageCaption,
					ImageInsert,
					ImageInsertViaUrl,
					ImageResize,
					ImageStyle,
					ImageToolbar,
					ImageUpload,
					Indent,
					IndentBlock,
					Italic,
					LineHeight,
					Link,
					LinkImage,
					List,
					ListProperties,
					MediaEmbed,
					Mention,
					Paragraph,
					PasteFromOffice,
					PasteFromOfficeEnhanced,
					PictureEditing,
					PresenceList,
					RealTimeCollaborativeComments,
					RealTimeCollaborativeEditing,
					RealTimeCollaborativeTrackChanges,
					RemoveFormat,
					SlashCommand,
					SpecialCharacters,
					SpecialCharactersArrows,
					SpecialCharactersCurrency,
					SpecialCharactersEssentials,
					SpecialCharactersLatin,
					SpecialCharactersMathematical,
					SpecialCharactersText,
					Strikethrough,
					Subscript,
					Superscript,
					Table,
					TableCaption,
					TableCellProperties,
					TableColumnResize,
					TableProperties,
					TableToolbar,
					TextTransformation,
					TodoList,
					TrackChanges,
					TrackChangesData,
					TrackChangesPreview,
					Underline
				],
				ai: {
					container: {
						type: 'sidebar',
						element: editorCkeditorAiRef.current,
						showResizeButton: false
					},
					chat: {
						context: {
							document: { enabled: true },
							urls: { enabled: true },
							files: { enabled: true }
						}
					}
				},
				balloonToolbar: [
					'comment',
					'|',
					'aiQuickActions',
					'|',
					'bold',
					'italic',
					'|',
					'link',
					'insertImage',
					'|',
					'bulletedList',
					'numberedList'
				],
				cloudServices: {
					tokenUrl: CLOUD_SERVICES_TOKEN_URL,
					webSocketUrl: CLOUD_SERVICES_WEBSOCKET_URL
				},
				collaboration: {
					channelId: DOCUMENT_ID
				},
				comments: {
					editorConfig: {
						extraPlugins: [Autoformat, Bold, Italic, List, Mention],
						mention: {
							feeds: [
								{
									marker: '@',
									feed: []
								}
							]
						}
					}
				},
				fontFamily: {
					supportAllValues: true
				},
				fontSize: {
					options: [10, 12, 14, 'default', 18, 20, 22],
					supportAllValues: true
				},
				fullscreen: {
					onEnterCallback: container =>
						container.classList.add(
							'editor-container',
							'editor-container_document-editor',
							'editor-container_include-annotations',
							'editor-container_contains-wrapper',
							'editor-container_include-fullscreen',
							'main-container'
						)
				},
				heading: {
					options: [
						{ model: 'paragraph', title: 'Paragraphe', class: 'ck-heading_paragraph' },
						{ model: 'heading1', view: 'h1', title: 'Lohateny 1', class: 'ck-heading_heading1' },
						{ model: 'heading2', view: 'h2', title: 'Lohateny 2', class: 'ck-heading_heading2' },
						{ model: 'heading3', view: 'h3', title: 'Lohateny 3', class: 'ck-heading_heading3' },
						{ model: 'heading4', view: 'h4', title: 'Lohateny 4', class: 'ck-heading_heading4' },
						{ model: 'heading5', view: 'h5', title: 'Lohateny 5', class: 'ck-heading_heading5' },
						{ model: 'heading6', view: 'h6', title: 'Lohateny 6', class: 'ck-heading_heading6' }
					]
				},
				image: {
					toolbar: [
						'toggleImageCaption',
						'|',
						'imageStyle:alignBlockLeft',
						'imageStyle:block',
						'imageStyle:alignBlockRight',
						'|',
						'resizeImage',
						'|',
						'ckboxImageEdit'
					],
					styles: {
						options: ['alignBlockLeft', 'block', 'alignBlockRight']
					}
				},
				// Nouveau texte initial, adapté au sujet
				initialData: `
					<h2>Mpamoaka lahatsoratra ho an'ny teny Malagasy</h2>
					<p>
						Ato no hanoratan'ny mpampiasa lahatsoratra amin'ny teny Malagasy.
						Ny tanjon'ny rafitra dia ny hanampy azy amin'ny:
					</p>
					<ul>
						<li>fanitsiana diso tsipelina sy fitsipika (oh: <strong>nb</strong>, <strong>mk</strong> tsy azo amin'ny fanombohan-teny),</li>
						<li>soso-kevitra amin'ny teny manaraka,</li>
						<li>fandikana sy famaritana teny (via API / rakibolana),</li>
						<li>famakafakana tsotra (sentiment, entités, sns.).</li>
					</ul>
					<p>Atombohy manoratra lahatsoratra fohy amin'ny teny Malagasy eto ambany.</p>
				`,
				licenseKey: LICENSE_KEY,
				lineHeight: {
					supportAllValues: true
				},
				link: {
					addTargetToExternalLinks: true,
					defaultProtocol: 'https://',
					decorators: {
						toggleDownloadable: {
							mode: 'manual',
							label: 'Téléchargeable',
							attributes: {
								download: 'file'
							}
						}
					}
				},
				list: {
					properties: {
						styles: true,
						startIndex: true,
						reversed: true
					}
				},
				mention: {
					feeds: [
						{
							marker: '@',
							feed: []
						}
					]
				},
				placeholder: 'Manomboka manoratra amin’ny teny Malagasy eto...',
				presenceList: {
					container: editorPresenceRef.current
				},
				sidebar: {
					container: editorAnnotationsRef.current
				},
				table: {
					contentToolbar: ['tableColumn', 'tableRow', 'mergeTableCells', 'tableProperties', 'tableCellProperties']
				}
			}
		};
	}, [isLayoutReady]);

	useEffect(() => {
		if (editorConfig) {
			configUpdateAlert(editorConfig);
		}
	}, [editorConfig]);
	// Composant pour afficher les erreurs
	const ErrorPanel = ({ errors }) => {
		if (errors.length === 0) {
			return (
				<div className="error-panel error-panel--success">
					✅ Tsy misy diso hita – Aucune erreur détectée
				</div>
			);
		}

		return (
			<div className="error-panel error-panel--warning">
				<div className="error-panel__header">
					⚠️ Diso {errors.length} hita – {errors.length} erreur(s) détectée(s)
				</div>
				<ul className="error-panel__list">
					{errors.map((err, index) => (
						<li key={index} className="error-panel__item">
							<span className="error-badge">{err.match}</span>
							<span className="error-message">{err.message}</span>
						</li>
					))}
				</ul>
			</div>
		);
	};
	return (
		
		<div className="main-container">
			<div className="app-header">
            <div className="brand">
                <div className="brand-icon">M</div>
                <span>Malagasy Editor</span>
            </div>
            <div className="presence" ref={editorPresenceRef}></div>
        </div>

        {/* ✅ NOUVEAU : Panel d'erreurs */}
        {/*<ErrorPanel errors={malagasyErrors} />*/}
			<div className="presence" ref={editorPresenceRef}></div>
			<div
				className="editor-container editor-container_document-editor editor-container_include-annotations editor-container_contains-wrapper editor-container_include-fullscreen"
				ref={editorContainerRef}
			>
				<div className="editor-container__menu-bar" ref={editorMenuBarRef}></div>
				<div className="editor-container__toolbar" ref={editorToolbarRef}></div>
				<div className="editor-container__editable-wrapper">
					<div className="editor-container__editor-wrapper">
						<div className="editor-container__editor">
							<div ref={editorRef}>
								{editorConfig && (
									/*<CKEditor
										editor={DecoupledEditor}
										config={editorConfig}
										onReady={editor => {
											editorToolbarRef.current.appendChild(editor.ui.view.toolbar.element);
											editorMenuBarRef.current.appendChild(editor.ui.view.menuBarView.element);
											editor.plugins.get('AnnotationsUIs').switchTo('narrowSidebar');

											// === Hook pour la vérification phonotactique ===
											editor.model.document.on('change:data', () => {
												const plainText = editor.getData().replace(/<[^>]+>/g, ' ');
												const errors = checkMalagasyRules(plainText);

												// ✅ NOUVEAU : Met à jour le state au lieu de console.log
												setMalagasyErrors(errors);
											});
										}}
										onAfterDestroy={() => {
											Array.from(editorToolbarRef.current.children).forEach(child => child.remove());
											Array.from(editorMenuBarRef.current.children).forEach(child => child.remove());
										}}
									/>*/

									<CKEditor
										onReady={editor => {
											editorToolbarRef.current.appendChild(editor.ui.view.toolbar.element);
											editorMenuBarRef.current.appendChild(editor.ui.view.menuBarView.element);

											// Switch the annotations UI to the narrow sidebar layout. If you remove this,
											// ensure that the container does not use the `editor-container__sidebar_narrow` CSS class,
											// since it corresponds to this display mode.
											editor.plugins.get('AnnotationsUIs').switchTo('narrowSidebar');

											//////////////////////////////////////////////////////////////
											// Écouter les frappes de touches
											editor.editing.view.document.on('keydown', (evt, data) => {
												console.log('Touche pressée:', data.key, data.keyCode);
											});
											
											// Écouter les changements de texte
											editor.model.document.on('change:data', () => {
												// Obtenir le texte sans balises HTML
												const htmlContent = editor.getData();
												const textOnly = htmlContent
												.replace(/<[^>]*>/g, '') // Enlever toutes les balises HTML
												.replace(/&nbsp;/g, ' ') // Remplacer &nbsp; par des espaces
												.replace(/&amp;/g, '&')  // Remplacer les entités HTML
												.trim();
												
												console.log('Texte sans balises:', textOnly);
												
												// Obtenir le dernier mot tapé
												const words = textOnly.split(/\s+/).filter(word => word.length > 0);
												const lastWord = words[words.length - 1];
												
												console.log('Dernier mot:', lastWord);
												console.log('Tous les mots:', words);
											});
											}}
											//////////////////////////////////////////////////////////
											
										onAfterDestroy={() => {
											Array.from(editorToolbarRef.current.children).forEach(child => child.remove());
											Array.from(editorMenuBarRef.current.children).forEach(child => child.remove());
										}}
										editor={DecoupledEditor}
										config={editorConfig}
									/>

								)}
							</div>
						</div>
						<div className="editor-container__sidebar editor-container__sidebar_narrow" ref={editorAnnotationsRef}></div>
					</div>
					<div className="editor-container__sidebar editor-container__sidebar_ckeditor-ai" ref={editorCkeditorAiRef}></div>
				</div>
			</div>
		</div>
	);
}

/* Fonction d’alerte premium (inchangée, tu peux la supprimer plus tard) */
function configUpdateAlert(config) {
	if (configUpdateAlert.configUpdateAlertShown) {
		return;
	}

	const isModifiedByUser = (currentValue, forbiddenValue) => {
		if (currentValue === forbiddenValue) {
			return false;
		}
		if (currentValue === undefined) {
			return false;
		}
		return true;
	};

	const valuesToUpdate = [];

	configUpdateAlert.configUpdateAlertShown = true;

	if (!isModifiedByUser(config.licenseKey, '<YOUR_LICENSE_KEY>')) {
		valuesToUpdate.push('LICENSE_KEY');
	}

	if (!isModifiedByUser(config.cloudServices?.tokenUrl, '<YOUR_CLOUD_SERVICES_TOKEN_URL>')) {
		valuesToUpdate.push('CLOUD_SERVICES_TOKEN_URL');
	}

	if (!isModifiedByUser(config.cloudServices?.webSocketUrl, '<YOUR_CLOUD_SERVICES_WEBSOCKET_URL>')) {
		valuesToUpdate.push('CLOUD_SERVICES_WEBSOCKET_URL');
	}

	if (valuesToUpdate.length) {
		window.alert(
			[
				'Please update the following values in your editor config',
				'to receive full access to Premium Features:',
				'',
				...valuesToUpdate.map(value => ` - ${value}`)
			].join('\n')
		);
	}
}