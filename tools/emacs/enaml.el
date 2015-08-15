;; enaml.el --- Major mode for editing Enaml files

;; define keywords unique to enaml
;; (python keywords will automatically be highlighted as well)
(defvar enaml-font-lock-keywords
  `(;; highlight these as keywords
    (,(regexp-opt '("enamldef" "template") 'words)
     1 font-lock-keyword-face)
    ;; highlight these as builtins
    (,(regexp-opt '("horizontal" "vertical" "hbox" "vbox"
		    "align" "spacer") 'words)
     1 font-lock-builtin-face)
    ;; highlight these as types
    (,(regexp-opt '("attr" "event") 'words)
     1 font-lock-type-face)
    ;; enamldefs
    (,(rx symbol-start (or "enamldef" "template") (1+ space) (group (1+ (or word ?_))))
     (1 font-lock-type-face)))
  "Additional font lock keywords for Enaml mode.")

;; Matches enaml block forms
(defconst enaml-block-start-rx
  (rx (or
       ;; Normal Python-style blocks (including enamldef)
       (sequence
        symbol-start
        (or "def" "class" "if" "elif" "else" "try"
            "except" "finally" "for" "while" "with"
            "enamldef" "template")
        symbol-end)
       ;; Any capitalized word following by ":"
       (sequence symbol-start upper (zero-or-more letter) symbol-end ":")
       ;; "::" at the end of a line
       (sequence (not (any ":")) "::" (or space eol)))))

;; Override python-indent-context to recognize enaml-specific block forms.
(defadvice python-indent-context (after
                                  enaml-indent-context
                                  activate)
  "Get information on indentation context in enaml-mode."
  (if (and (eq major-mode 'enaml-mode)
           ;; These cases take precedence.
           (not (or (eq ad-return-value 'no-indent)
                    (eq ad-return-value 'inside-string)
                    (eq ad-return-value 'inside-paren)
                    (eq ad-return-value 'after-backslash))))
      ;; The 'after-beginning-of-block case is identical to python-indent-context,
      ;; but uses our block start regex instead.
    (let ((start (save-excursion
                   (when (progn
                           (back-to-indentation)
                           (python-util-forward-comment -1)
                           (equal (char-before) ?:))
                     (while (and (re-search-backward
                                  enaml-block-start-rx nil t)
                                 (or
                                  (python-syntax-context-type)
                                  (python-info-continuation-line-p))))
                     (when (looking-at enaml-block-start-rx)
                       (point-marker))))))
      (if start (setq ad-return-value (cons 'after-beginning-of-block  start))))))

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
