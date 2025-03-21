package br.mp.mprn.gaeco.custodiatech.repository.auth;

import br.mp.mprn.gaeco.custodiatech.model.auth.AceiteTermo;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.PagingAndSortingRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface AceiteTermoRepository extends PagingAndSortingRepository<AceiteTermo, Long>,
        JpaSpecificationExecutor<AceiteTermo>, CrudRepository<AceiteTermo, Long> {

     Optional<AceiteTermo> findFirstByIdUsuarioAceiteAndModulo(Long idUsuarioAceite, String modulo);
}
