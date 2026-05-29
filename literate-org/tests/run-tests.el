;;; run-tests.el --- Batch harness for literate-org ert tests  -*- lexical-binding: t; -*-

;;; Commentary:
;;
;; Loads literate-org.org (and the deps it relies on but does not
;; explicitly require — cl/anaphora/dired) from the user's straight
;; build tree, then runs the ert tests matching the selector in
;; $LITERATE_ORG_TEST_SELECTOR (default "test-tf").
;;
;;   emacs -Q --batch -L . -l tests/run-tests.el \
;;         -f ert-run-tests-batch-and-exit
;;
;; or via the Makefile:  make test-terraform
;;
;; The straight build path is overridable with $STRAIGHT_BUILD_DIR so
;; this harness is not pinned to one machine.

;;; Code:

(let ((build (or (getenv "STRAIGHT_BUILD_DIR")
                 (expand-file-name "~/.emacs.d/straight/build/"))))
  (when (file-directory-p build)
    (dolist (d (directory-files build t "\\`[^.]"))
      (when (file-directory-p d) (add-to-list 'load-path d)))))

(let ((le (or (getenv "LITERATE_ELISP_DIR")
              (expand-file-name "~/projects/literate-elisp"))))
  (when (file-directory-p le) (add-to-list 'load-path le)))

(require 'literate-elisp)
(require 'cl-lib)
;; literate-org.org relies on the classic `cl' aliases (first / loop) and
;; on anaphora (awhen / aand) + dired (dired-replace-in-string) being
;; loaded ambiently — they are in an interactive session but not under -Q.
(with-no-warnings (require 'cl))
(require 'anaphora)
(require 'dired)

;; All ert tests are embedded in literate-org.org (tests-embedded-in-
;; narrative) — loading the .org defines them.
(let ((root (file-name-directory
             (directory-file-name
              (file-name-directory (or load-file-name buffer-file-name))))))
  (condition-case e
      (literate-elisp-load (expand-file-name "literate-org.org" root))
    (error (princ (format "LOAD-ERR: %s\n" e)) (kill-emacs 3))))

(setq ert-batch-print-level 5)

;;; run-tests.el ends here
