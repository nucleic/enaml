;; enaml.el --- Major mode for editing Enaml files

;; define keywords unique to enaml
;; (python keywords will automatically be highlighted as well)
(defvar enaml-font-lock-keywords
  `(;; highlight these as keywords
    (,(regexp-opt '("enamldef") 'words)
     1 font-lock-keyword-face)
    ;; highlight these as builtins
    (,(regexp-opt '("horizontal" "vertical" "hbox" "vbox"
		    "align" "spacer") 'words)
     1 font-lock-builtin-face)
    ;; highlight these as types
    (,(regexp-opt '("attr" "event") 'words)
     1 font-lock-type-face)
    ;; enamldefs
    (,(rx symbol-start "enamldef" (1+ space) (group (1+ (or word ?_))))
     (1 font-lock-type-face)))
  "Additional font lock keywords for Enaml mode.")

(define-derived-mode
  enaml-mode python-mode "Enaml"
  "Major mode for editing Enaml files"
  (setcar font-lock-defaults
          (if (boundp 'python-font-lock-keywords)
              ;; support python.el
              (append python-font-lock-keywords enaml-font-lock-keywords)
            ;; support python-mode.el
            (append py-font-lock-keywords enaml-font-lock-keywords))))

(add-to-list 'auto-mode-alist '("\\.enaml\\'" . enaml-mode))

(provide 'enaml)
